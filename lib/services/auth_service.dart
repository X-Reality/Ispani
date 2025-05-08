// lib/services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';

class AuthService {
  static const String baseUrl = 'http://127.0.0.1:8000/';
  static final FlutterSecureStorage _secureStorage = FlutterSecureStorage();

  // Store tokens
  static Future<void> _saveTokens(
      String accessToken, String refreshToken) async {
    await _secureStorage.write(key: 'access_token', value: accessToken);
    await _secureStorage.write(key: 'refresh_token', value: refreshToken);
  }

  static Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: 'access_token');
  }

  static Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: 'refresh_token');
  }

  static Future<void> clearTokens() async {
    await _secureStorage.delete(key: 'access_token');
    await _secureStorage.delete(key: 'refresh_token');
  }

  static Future<bool> refreshTokenIfNeeded() async {
    final refreshToken = await getRefreshToken();

    if (refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await _saveTokens(data['access'], refreshToken);
        return true;
      }
    } catch (_) {}
    return false;
  }

  // Save user data
  static Future<void> saveUserData(Map<String, dynamic> userData) async {
    await _secureStorage.write(key: 'user_data', value: jsonEncode(userData));
  }

  // Get user data
  static Future<Map<String, dynamic>?> getUserData() async {
    final userData = await _secureStorage.read(key: 'user_data');
    if (userData != null) {
      return jsonDecode(userData) as Map<String, dynamic>;
    }
    return null;
  }

  Future<Map<String, dynamic>> signup(
      String username, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/signup/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(
            {'username': username, 'email': email, 'password': password}),
      );

      return {
        'success': response.statusCode == 200 || response.statusCode == 201,
        'statusCode': response.statusCode,
        'response': jsonDecode(response.body),
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Login
  static Future<Map<String, dynamic>> login(
      String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        // Save tokens and user data
        await _saveTokens(
            responseData['token']['access'], responseData['token']['refresh']);
        await saveUserData(responseData['user']);

        return {
          'success': true,
          'message': responseData['message'],
          'user': responseData['user'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Login failed. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // Sign up step 1: Send OTP
  static Future<Map<String, dynamic>> requestOtp(
      String email, String password, String username) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/signup/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'username': username,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': true,
          'message': responseData['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Failed to send OTP. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // Sign up step 2: Verify OTP
  static Future<Map<String, dynamic>> verifyOtp(
      String email, String otp) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/verify-otp/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'otp': otp,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': true,
          'message': responseData['message'],
          'temp_token': responseData['temp_token'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Invalid OTP. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // Sign up step 3: Complete registration
  static Future<Map<String, dynamic>> completeRegistration(String tempToken,
      List<String> roles, Map<String, dynamic> profileData) async {
    try {
      // Combine data into one request payload
      final Map<String, dynamic> requestData = {
        'temp_token': tempToken,
        'roles': roles,
        ...profileData,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/auth/complete-registration/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestData),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        // Save tokens and user data
        await _saveTokens(
            responseData['token']['access'], responseData['token']['refresh']);
        await saveUserData(responseData['user']);

        return {
          'success': true,
          'message': responseData['message'],
          'user': responseData['user'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Registration failed. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<bool> isAccessTokenExpired() async {
    final token = await getAccessToken();
    if (token == null) return true;
    return JwtDecoder.isExpired(token);
  }

  static Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    if (token == null || JwtDecoder.isExpired(token)) {
      return await refreshTokenIfNeeded();
    }
    return true;
  }

  // Forgot Password: Request reset
  static Future<Map<String, dynamic>> requestPasswordReset(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/forgot-password/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': true,
          'message': responseData['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message': error['error'] ??
              'Failed to request password reset. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // Forgot Password: Confirm reset
  static Future<Map<String, dynamic>> confirmPasswordReset(
      String uid, String token, String newPassword) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/reset-password/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'uid': uid,
          'token': token,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': true,
          'message': responseData['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'message':
              error['error'] ?? 'Failed to reset password. Please try again.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // Logout
  static Future<Map<String, dynamic>> logout() async {
    try {
      final token = await getAccessToken();

      if (token == null) {
        await clearTokens();
        return {
          'success': true,
          'message': 'Logged out successfully',
        };
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/logout/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      // Clear local storage regardless of server response
      await clearTokens();

      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': 'Logged out successfully',
        };
      } else {
        return {
          'success':
              true, // Still consider this a success since we cleared local tokens
          'message': 'Logged out successfully',
        };
      }
    } catch (e) {
      // Even if API call fails, clear tokens locally
      await clearTokens();
      return {
        'success':
            true, // Still consider this a success since we cleared local tokens
        'message': 'Logged out successfully',
      };
    }
  }
}
