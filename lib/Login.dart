import 'package:flutter/material.dart';
import 'package:ispani/Forgotpassword.dart';
import 'package:ispani/SignUp.dart';
import 'package:ispani/HomeScreen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html;

import 'package:shared_preferences/shared_preferences.dart'; // For web storage fallback

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: LoginScreen(),
  ));
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool isChecked = false;
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  // Storage solutions
  final FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  bool _isWeb = false;

  @override
  void initState() {
    super.initState();
    // Check if we're running on web
    try {
      _isWeb = identical(0, 0.0);
    } catch (e) {
      _isWeb = false;
    }
  }

  // Method to safely store token
  Future<void> storeTokens(String accessToken, String refreshToken,
      String username, String email) async {
    if (_isWeb) {
      // Use localStorage for web
      html.window.localStorage['access_token'] = accessToken;
      html.window.localStorage['refresh_token'] = refreshToken;
      html.window.localStorage['username'] = username;
      html.window.localStorage['email'] = email;
    } else {
      // Use secure storage for mobile
      try {
        await _secureStorage.write(key: 'access_token', value: accessToken);
        await _secureStorage.write(key: 'refresh_token', value: refreshToken);
        await _secureStorage.write(key: 'username', value: username);
        await _secureStorage.write(key: 'email', value: email);
      } catch (e) {
        print("Secure storage error: $e");
        // Fallback to localStorage if secure storage fails
        html.window.localStorage['access_token'] = accessToken;
        html.window.localStorage['refresh_token'] = refreshToken;
        html.window.localStorage['username'] = username;
        html.window.localStorage['email'] = email;
      }
    }
  }

  Future<void> _validateAndLogin() async {
    if (_formKey.currentState?.validate() ?? false) {
      // Show a loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => Center(child: CircularProgressIndicator()),
      );

      // Prepare the data for the API request
      String email = _emailController.text;
      String password = _passwordController.text;

      // Send the login request to your backend
      try {
        final response = await http.post(
          Uri.parse('http://127.0.0.1:8000/login/'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'email': email,
            'password': password,
          }),
        );

        // Close the loading indicator
        Navigator.pop(context);

        if (response.statusCode == 200) {
          // Parse the response if successful
          final responseBody = json.decode(response.body);
          final Map<String, dynamic> responseData = json.decode(response.body);

          SharedPreferences prefs = await SharedPreferences.getInstance();
          await prefs.setString(
              "access_token", responseData["token"]["access"]); // Save token

          // Check if the response contains a success message
          if (responseBody['message'] == 'Login successful') {
            // Store authentication tokens
            if (responseBody.containsKey('token') &&
                responseBody.containsKey('user')) {
              await storeTokens(
                  responseBody['token']['access'],
                  responseBody['token']['refresh'],
                  responseBody['user']['username'],
                  responseBody['user']['email']);
            }

            // Navigate to HomeScreen
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => HomeScreen()),
            );
          } else {
            // Show error message if login failed
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                  content: Text(responseBody['message'] ?? 'Login failed')),
            );
          }
        } else {
          // Parse error response
          final errorBody = json.decode(response.body);

          // Show error message for non-200 status codes
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text(
                    errorBody['error'] ?? 'An error occurred during login')),
          );
        }
      } catch (e) {
        // Close the loading indicator on error
        Navigator.pop(context);

        // Show error message if request fails
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to connect to the server')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              height: 300,
              decoration: BoxDecoration(
                image: DecorationImage(
                  image: AssetImage("assets/3203866.jpg"),
                  fit: BoxFit.cover,
                ),
              ),
              child: Center(
                child: Text(
                  "",
                  textAlign: TextAlign.left,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            Transform.translate(
              offset: Offset(0, -50),
              child: Container(
                width: double.infinity,
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(20),
                    topRight: Radius.circular(20),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black26,
                      blurRadius: 10,
                      offset: Offset(0, -4),
                    ),
                  ],
                ),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Welcome Back',
                        style: TextStyle(
                          fontSize: 35,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 10),
                      Text(
                        'Please enter your credentials to continue.',
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _emailController,
                        decoration: InputDecoration(
                          labelText: "Email",
                          hintText: "Enter your email",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return "Email is required";
                          } else if (!RegExp(r'^[^@]+@[^@]+\.[^@]+')
                              .hasMatch(value)) {
                            return "Enter a valid email";
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: InputDecoration(
                          labelText: "Password",
                          hintText: "Enter your password",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return "Password is required";
                          } else if (value.length < 6) {
                            return "Password must be at least 6 characters";
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Checkbox(
                                value: isChecked,
                                onChanged: (bool? value) {
                                  setState(() {
                                    isChecked = value!;
                                  });
                                },
                              ),
                              Text("Remember Me"),
                            ],
                          ),
                          InkWell(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (context) => Forgotpassword()),
                              );
                            },
                            child: Text(
                              'Forgot Password?',
                              style: TextStyle(
                                  color: Colors.blue,
                                  fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 30),
                      ElevatedButton(
                        onPressed: _validateAndLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color.fromARGB(255, 147, 182, 138),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          minimumSize: Size(double.infinity, 50),
                        ),
                        child: Text(
                          'Login',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      ),
                      SizedBox(height: 20),
                      Center(
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('Don\'t have an account? '),
                            InkWell(
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                      builder: (context) => SignupScreen()),
                                );
                              },
                              child: Text(
                                'Sign up',
                                style: TextStyle(
                                    color: Color.fromARGB(255, 147, 182, 138)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
