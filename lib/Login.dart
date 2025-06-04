import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:ispani/Forgotpassword.dart';
import 'package:ispani/HomeScreen.dart';
import 'package:ispani/SignUp.dart';
import 'package:ispani/TutorHomeScreen.dart';

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

  final LocalAuthentication auth = LocalAuthentication();

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<bool> _authenticateWithBiometrics() async {
    try {
      final bool canAuthenticate = await auth.canCheckBiometrics || await auth.isDeviceSupported();

      if (!canAuthenticate) return false;

      return await auth.authenticate(
        localizedReason: 'Authenticate to login',
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
        ),
      );
    } catch (e) {
      print("Biometric auth error: $e");
      return false;
    }
  }

  Future<void> _handleLogin(Widget screen, String message) async {
    if (_formKey.currentState!.validate()) {
      final success = await _authenticateWithBiometrics();
      if (!success) {
        _showSnackbar("Biometric authentication failed");
        return;
      }

      _showSnackbar(message);
      setState(() {
        _isLoading = true;
      });

      await Future.delayed(Duration(milliseconds: 1500));

      setState(() {
        _isLoading = false;
      });

      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => screen),
      );
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
                // Background image
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
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                      boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, -4))],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          Text('Welcome Back', style: TextStyle(fontSize: 35, fontWeight: FontWeight.bold)),
                          SizedBox(height: 10),
                          Text('Please enter your credentials to continue.'),
                          SizedBox(height: 20),

                          // Email
                          TextFormField(
                            controller: _emailController,
                            decoration: InputDecoration(
                              labelText: "Email",
                              hintText: "Enter your email",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                              filled: true,
                              fillColor: Colors.white,
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) return "Email is required";
                              if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(value)) return "Enter a valid email";
                              return null;
                            },
                          ),
                          SizedBox(height: 20),

                          // Password
                          TextFormField(
                            controller: _passwordController,
                            obscureText: true,
                            decoration: InputDecoration(
                              labelText: "Password",
                              hintText: "Enter your password",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                              filled: true,
                              fillColor: Colors.white,
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) return "Password is required";
                              if (value.length < 6) return "Password must be at least 6 characters";
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
                                    onChanged: (value) => setState(() => isChecked = value!),
                                  ),
                                  Text("Remember Me"),
                                ],
                              ),
                              InkWell(
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => Forgotpassword()),
                                ),
                                child: Text(
                                  'Forgot Password?',
                                  style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // Login
                          GestureDetector(
                            onTap: () => _handleLogin(HomeScreen(), 'Logging in...'),
                            onDoubleTap: () => _handleLogin(TutorHomeScreen(), 'Logging in as tutor...'),
                            child: ElevatedButton(
                              onPressed: null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Color.fromARGB(255, 147, 182, 138),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                minimumSize: Size(double.infinity, 50),
                              ),
                              child: Text('Login', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                            ),
                          ),
                          SizedBox(height: 20),

                          // Sign up
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text("Don't have an account? "),
                              InkWell(
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => SignupScreen()),
                                ),
                                child: Text('Sign up', style: TextStyle(color: Color.fromARGB(255, 147, 182, 138))),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // OR Divider
                          Stack(
                            children: [
                              Divider(),
                              Center(
                                child: Container(
                                  width: 60,
                                  color: Colors.white,
                                  child: Text('OR', textAlign: TextAlign.center),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 36),

                          // Social Logins (placeholders)
                          _socialLoginButton(Icons.facebook_outlined, "Sign in with Facebook"),
                          _socialLoginButton(Icons.face, "Sign in with Google"),
                          _socialLoginButton(Icons.apple, "Sign in with Apple"),
                          SizedBox(height: 30),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          if (_isLoading)
            Container(
              color: Colors.black38,
              child: Center(child: CircularProgressIndicator()),
            ),
        ],
      ),
    );
  }

  Widget _socialLoginButton(IconData icon, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: ElevatedButton(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          side: BorderSide(color: Colors.grey),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          minimumSize: Size(double.infinity, 50),
          alignment: Alignment.centerLeft,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.black),
            SizedBox(width: 10),
            Text(label, style: TextStyle(color: Colors.black)),
          ],
        ),
      ),
    );
  }
}
