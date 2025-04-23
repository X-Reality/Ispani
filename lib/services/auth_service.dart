import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final FlutterSecureStorage _storage = FlutterSecureStorage();
  final String _baseUrl = 'http://127.0.0.1:8000';

  // Consistent key names
  static const String ACCESS_TOKEN_KEY = 'access_token';
  static const String REFRESH_TOKEN_KEY = 'refresh_token';
  static const String USER_ID_KEY = 'user_id';

  // Store authentication tokens
  Future<void> storeTokens({
    required String accessToken,
    required String refreshToken,
    required String userId,
  }) async {
    await _storage.write(key: ACCESS_TOKEN_KEY, value: accessToken);
    await _storage.write(key: REFRESH_TOKEN_KEY, value: refreshToken);
    await _storage.write(key: USER_ID_KEY, value: userId);
  }

  // Get access token
  Future<String?> getAccessToken() async {
    return await _storage.read(key: ACCESS_TOKEN_KEY);
  }

  // Get refresh token
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: REFRESH_TOKEN_KEY);
  }

  // Get user ID
  Future<String?> getUserId() async {
    return await _storage.read(key: USER_ID_KEY);
  }

  // Clear all tokens (for logout)
  Future<void> logout() async {
    await _storage.deleteAll();
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  // Sign up
  Future<Map<String, dynamic>> signup(
      String username, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/signup/'),
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

  // Verify OTP
  Future<Map<String, dynamic>> verifyOtp(String email, String otp) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/verify-otp/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'otp': otp}),
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        if (responseData.containsKey('access') &&
            responseData.containsKey('refresh') &&
            responseData.containsKey('user')) {
          await storeTokens(
            accessToken: responseData['access'],
            refreshToken: responseData['refresh'],
            userId: responseData['user']['id'].toString(),
          );
        }
      }

      return {
        'success': response.statusCode == 200 || response.statusCode == 201,
        'statusCode': response.statusCode,
        'response': responseData,
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Login
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['message'] == 'Login successful') {
        if (data.containsKey('access') &&
            data.containsKey('refresh') &&
            data.containsKey('user')) {
          await storeTokens(
            accessToken: data['access'],
            refreshToken: data['refresh'],
            userId: data['user']['id'].toString(),
          );
        }
      }

      return {
        'success':
            response.statusCode == 200 && data['message'] == 'Login successful',
        'statusCode': response.statusCode,
        'response': data,
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Submit registration form
  Future<Map<String, dynamic>> submitRegistration(
      Map<String, dynamic> formData) async {
    try {
      final token = await getAccessToken();

      if (token == null || token.isEmpty) {
        return {'success': false, 'error': 'Authentication token is missing'};
      }

      final response = await http.post(
        Uri.parse('$_baseUrl/auth/complete-registration/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(formData),
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
}
