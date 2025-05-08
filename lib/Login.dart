import 'package:flutter/material.dart';
import 'package:ispani/Forgotpassword.dart';
import 'package:ispani/HomeScreen.dart';
import 'package:ispani/SignUp.dart';
import 'package:ispani/TutorHomeScreen.dart';
import 'package:ispani/services/auth_service.dart';
import 'package:url_launcher/url_launcher.dart';

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

  bool _isLoading = false;
  String _errorMessage = '';

  void _showSnackbar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : null,
      ),
    );
  }

  // Handle login with backend integration
  Future<void> _handleLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _errorMessage = '';
      });

      try {
        final result = await AuthService.login(
          _emailController.text.trim(),
          _passwordController.text,
        );

        setState(() {
          _isLoading = false;
        });

        if (result['success']) {
          _showSnackbar(result['message'] ?? 'Login successful');

          // Check user roles to determine which screen to navigate to
          final userData = await AuthService.getUserData();
          if (userData != null && userData['role'] != null) {
            final roles = List<String>.from(userData['role']);

            if (roles.contains('tutor')) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => TutorHomeScreen()),
              );
            } else {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => HomeScreen()),
              );
            }
          } else {
            // Default to HomeScreen if role information is not available
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => HomeScreen()),
            );
          }
        } else {
          setState(() {
            _errorMessage = result['message'] ?? 'Login failed';
          });
          _showSnackbar(_errorMessage, isError: true);
        }
      } catch (e) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'An error occurred. Please try again.';
        });
        _showSnackbar(_errorMessage, isError: true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Column(
              children: [
                // Background Image
                Container(
                  width: double.infinity,
                  height: 300,
                  decoration: BoxDecoration(
                    image: DecorationImage(
                      image: AssetImage("assets/3203866.jpg"),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),

                // Login Form
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
                        children: [
                          Text(
                            'Welcome Back',
                            style: TextStyle(
                                fontSize: 35, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 10),
                          Text('Please enter your credentials to continue.'),
                          SizedBox(height: 20),

                          // Display error message if any
                          if (_errorMessage.isNotEmpty)
                            Container(
                              padding: EdgeInsets.all(10),
                              margin: EdgeInsets.only(bottom: 20),
                              decoration: BoxDecoration(
                                color: Colors.red.shade50,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.red.shade200),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.error_outline, color: Colors.red),
                                  SizedBox(width: 10),
                                  Expanded(
                                    child: Text(
                                      _errorMessage,
                                      style:
                                          TextStyle(color: Colors.red.shade700),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          // Email Field
                          TextFormField(
                            controller: _emailController,
                            decoration: InputDecoration(
                              labelText: "Email",
                              hintText: "Enter your email",
                              border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10)),
                              filled: true,
                              fillColor: Colors.white,
                              prefixIcon: Icon(Icons.email),
                            ),
                            keyboardType: TextInputType.emailAddress,
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

                          // Password Field
                          TextFormField(
                            controller: _passwordController,
                            obscureText: true,
                            decoration: InputDecoration(
                              labelText: "Password",
                              hintText: "Enter your password",
                              border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10)),
                              filled: true,
                              fillColor: Colors.white,
                              prefixIcon: Icon(Icons.lock),
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
                                children: [
                                  Checkbox(
                                    value: isChecked,
                                    onChanged: (value) {
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
                                          builder: (context) =>
                                              Forgotpassword()));
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

                          // Login Button
                          ElevatedButton(
                            onPressed: _isLoading ? null : _handleLogin,
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  Color.fromARGB(255, 147, 182, 138),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12)),
                              minimumSize: Size(double.infinity, 50),
                            ),
                            child: _isLoading
                                ? SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : Text(
                                    'Login',
                                    style: TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18),
                                  ),
                          ),
                          SizedBox(height: 20),

                          // Sign up
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text('Don\'t have an account? '),
                              InkWell(
                                onTap: () async {
                                  const url = 'http://localhost:3000/';
                                  if (await canLaunchUrl(Uri.parse(url))) {
                                    await launchUrl(Uri.parse(url),
                                        mode: LaunchMode.externalApplication);
                                  } else {
                                    throw 'Could not launch $url';
                                  }
                                },
                                child: Text(
                                  'Sign up',
                                  style: TextStyle(
                                      color:
                                          Color.fromARGB(255, 147, 182, 138)),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // OR Divider
                          Stack(
                            alignment: Alignment.center,
                            children: [
                              Divider(),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 10),
                                color: Colors.white,
                                child: Text('OR', textAlign: TextAlign.center),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // Social Login Buttons
                          _buildSocialLoginButton(
                            icon: Icons.facebook,
                            text: "Continue with Facebook",
                            onPressed: () => _handleSocialLogin("facebook"),
                          ),
                          SizedBox(height: 16),

                          _buildSocialLoginButton(
                            icon: Icons.g_mobiledata,
                            text: "Continue with Google",
                            onPressed: () => _handleSocialLogin("google"),
                          ),
                          SizedBox(height: 16),

                          _buildSocialLoginButton(
                            icon: Icons.apple,
                            text: "Continue with Apple",
                            onPressed: () => _handleSocialLogin("apple"),
                          ),
                          SizedBox(height: 30),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Spinner Overlay - Now handled by the button itself
        ],
      ),
    );
  }

  // Helper method to build social login buttons
  Widget _buildSocialLoginButton({
    required IconData icon,
    required String text,
    required VoidCallback onPressed,
  }) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        side: BorderSide(color: Colors.grey.shade300),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        minimumSize: Size(double.infinity, 50),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon),
          SizedBox(width: 12),
          Text(text),
        ],
      ),
    );
  }

  // Handle social login (placeholder for now)
  void _handleSocialLogin(String provider) {
    _showSnackbar("$provider login not implemented yet");
    // Here you would integrate with social auth providers
  }
}
