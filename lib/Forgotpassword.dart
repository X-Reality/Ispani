import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: Forgotpassword(),
  ));
}

const String baseUrl = "http://yourbackend.com";

class Forgotpassword extends StatefulWidget {
  const Forgotpassword({super.key});

  @override
  State<Forgotpassword> createState() => _ForgotpasswordState();
}

class _ForgotpasswordState extends State<Forgotpassword> {
  final TextEditingController _emailController = TextEditingController();
  bool _loading = false;

  Future<void> _requestPasswordReset() async {
    final email = _emailController.text.trim();

    if (email.isEmpty) {
      _showDialog("Please enter your email.");
      return;
    }

    setState(() => _loading = true);

    try {
      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/auth/forgot-password/"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _showDialog(data['message'] ?? "Check your email for reset link.");
      } else {
        _showDialog(data['error'] ?? "Something went wrong.");
      }
    } catch (e) {
      _showDialog("Network error. Please try again.");
    } finally {
      setState(() => _loading = false);
    }
  }

  void _showDialog(String message) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("Reset Password"),
        content: Text(message),
        actions: [
          TextButton(
            child: Text("OK"),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: EdgeInsets.all(30),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 60,
                backgroundColor: Color.fromARGB(255, 147, 182, 138),
                child:
                    Icon(Icons.email_outlined, size: 50, color: Colors.black),
              ),
              SizedBox(height: 36),
              Text(
                'Forgot Password',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.bold,
                  fontFamily: 'Poppins',
                ),
              ),
              SizedBox(height: 30),
              TextField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: "Email",
                  hintText: "Enter your Email",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
              SizedBox(height: 30),
              ElevatedButton(
                onPressed: _loading ? null : _requestPasswordReset,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color.fromARGB(255, 147, 182, 138),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  minimumSize: Size(double.infinity, 50),
                ),
                child: _loading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text(
                        'Reset password',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
