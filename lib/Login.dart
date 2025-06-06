import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
  final LocalAuthentication auth = LocalAuthentication();
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool _isLoading = false;

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<bool> _authenticateWithBiometrics() async {
    try {
      final bool canAuthenticate = await auth.canCheckBiometrics || await auth.isDeviceSupported();
      if (!canAuthenticate) return false;

      return await auth.authenticate(
        localizedReason: 'Authenticate to login',
        options: const AuthenticationOptions(biometricOnly: true, stickyAuth: true),
      );
    } catch (e) {
      debugPrint("Biometric auth error: $e");
      return false;
    }
  }

  Future<bool> _checkFallbackPIN() async {
    final storedPin = await secureStorage.read(key: 'fallback_pin');

    if (storedPin == null) {
      _showSnackbar("Biometric failed and no fallback PIN found.");
      return false;
    }

    String? userPin = await _showPinDialog();
    return userPin == storedPin;
  }

  Future<String?> _showPinDialog() async {
    String? pin;
    return showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        final TextEditingController pinController = TextEditingController();
        return AlertDialog(
          title: const Text('Enter Fallback PIN'),
          content: TextField(
            controller: pinController,
            keyboardType: TextInputType.number,
            obscureText: true,
            maxLength: 6,
            decoration: const InputDecoration(hintText: 'Enter your 6-digit PIN'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(), // cancel
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                pin = pinController.text;
                Navigator.of(context).pop(pin);
              },
              child: const Text('Submit'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _handleLogin(Widget screen, String message, String role) async {
    if (_formKey.currentState!.validate()) {
      final bioSuccess = await _authenticateWithBiometrics();

      if (!bioSuccess) {
        final fallbackSuccess = await _checkFallbackPIN();
        if (!fallbackSuccess) {
          _showSnackbar("Authentication failed.");
          return;
        }
      }

      _showSnackbar(message);

      setState(() => _isLoading = true);

      // Save login state and role in SharedPreferences
      SharedPreferences prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isLoggedIn', true);
      await prefs.setString('userRole', role);

      await Future.delayed(const Duration(milliseconds: 1500));
      setState(() => _isLoading = false);

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => screen),
      );
    }
  }

  Widget _socialLoginButton(IconData icon, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: ElevatedButton(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          side: const BorderSide(color: Colors.grey),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          minimumSize: const Size(double.infinity, 50),
          alignment: Alignment.centerLeft,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.black),
            const SizedBox(width: 10),
            Text(label, style: const TextStyle(color: Colors.black)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  height: 300,
                  decoration: const BoxDecoration(
                    image: DecorationImage(
                      image: AssetImage("assets/3203866.jpg"),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                Transform.translate(
                  offset: const Offset(0, -50),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: const BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                      boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, -4))],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          const Text('Welcome Back', style: TextStyle(fontSize: 35, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 10),
                          const Text('Please enter your credentials to continue.'),
                          const SizedBox(height: 20),

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
                          const SizedBox(height: 20),

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
                          const SizedBox(height: 10),

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Checkbox(
                                    value: isChecked,
                                    onChanged: (value) => setState(() => isChecked = value!),
                                  ),
                                  const Text("Remember Me"),
                                ],
                              ),
                              InkWell(
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => const Forgotpassword()),
                                ),
                                child: const Text(
                                  'Forgot Password?',
                                  style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 30),

                          // Login button with tap and double tap
                          GestureDetector(
                            onTap: () => _handleLogin( HomeScreen(), 'Logging in as student...', 'student'),
                            onDoubleTap: () => _handleLogin(const TutorHomeScreen(), 'Logging in as tutor...', 'tutor'),
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color.fromARGB(255, 147, 182, 138),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              padding: const EdgeInsets.symmetric(vertical: 15),
                              alignment: Alignment.center,
                              child: const Text(
                                'Login',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                ),
                              ),
                            ),
                          ),

                          const SizedBox(height: 20),

                          // Sign up link
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Text("Don't have an account? "),
                              InkWell(
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => const SignupScreen()),
                                ),
                                child: const Text(
                                  'Sign up',
                                  style: TextStyle(color: Color.fromARGB(255, 147, 182, 138)),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 30),

                          // OR divider
                          Stack(
                            children: const [
                              Divider(),
                              Center(
                                child: SizedBox(
                                  width: 60,
                                  child: Text('OR', textAlign: TextAlign.center),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 36),

                          // Social login buttons placeholders
                          _socialLoginButton(Icons.facebook_outlined, "Sign in with Facebook"),
                          _socialLoginButton(Icons.face, "Sign in with Google"),
                          _socialLoginButton(Icons.apple, "Sign in with Apple"),
                          const SizedBox(height: 30),
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
              child: const Center(child: CircularProgressIndicator()),
            ),
        ],
      ),
    );
  }
}
