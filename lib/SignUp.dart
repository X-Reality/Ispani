import 'package:flutter/material.dart';
import 'package:ispani/Login.dart';
import 'package:ispani/Otp.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: SignupScreen(),
  ));
}

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>(); // Key for form validation
  final TextEditingController _emailController = TextEditingController();

  bool _isLoading = false; // Show loading indicator during OTP send

  // Simulate sending OTP to email (replace this with your real API call)
  Future<bool> sendOtpToEmail(String email) async {
    await Future.delayed(Duration(seconds: 2)); // simulate network delay
    // In real app, call API here, e.g.:
    // final response = await http.post(Uri.parse('https://yourapi/sendotp'), body: {'email': email});
    // return response.statusCode == 200;
    return true; // Assume success
  }

  void _validateAndSendOtp() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    final email = _emailController.text.trim();

    bool success = await sendOtpToEmail(email);

    setState(() {
      _isLoading = false;
    });

    if (success) {
      // Navigate to OtpScreen, pass email
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => OtpScreen(email: email),
        ),
      );
    } else {
      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send OTP. Please try again.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
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
              child: Center(
                child: Text(
                  "",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            // Move Form Up to Overlap Background
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
                        'Create an Account',
                        style: TextStyle(
                          fontSize: 35,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 10),
                      Text(
                        'Please enter your email to continue.',
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 20),

                      // Email TextField
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
                          } else if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(value)) {
                            return "Enter a valid email";
                          }
                          return null;
                        },
                      ),

                      SizedBox(height: 30),

                      _isLoading
                          ? CircularProgressIndicator()
                          : ElevatedButton(
                        onPressed: _validateAndSendOtp,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color.fromARGB(255, 147, 182, 138),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          minimumSize: Size(double.infinity, 50),
                        ),
                        child: Text(
                          'Send OTP',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      ),

                      SizedBox(height: 270),
                      Center(
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('Have an account, '),
                            InkWell(
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => LoginScreen()),
                                );
                              },
                              child: Text(
                                'Log in',
                                style: TextStyle(color: Color.fromARGB(255, 147, 182, 138)),
                              ),
                            )
                          ],
                        ),
                      ),
                      SizedBox(height: 10),
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
