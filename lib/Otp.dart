import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ispani/Register.dart';

class OtpScreen extends StatefulWidget {
  final String email; // Receive email from previous screen
  final String password; // Add password parameter
  const OtpScreen({super.key, required this.email, required this.password});

  
  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  int _seconds = 60;
  Timer? _timer;
  final TextEditingController _otpController = TextEditingController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    startTimer();
    
  }

  void startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_seconds > 0) {
        setState(() {
          _seconds--;
        });
      } else {
        _timer!.cancel();
      }
    });
  }


  // Function to verify OTP with Django backend
Future<void> verifyOTP() async {
  setState(() {
    _isLoading = true;
  });

  const url = "http://127.0.0.1:8000/verify-otp/";
  try {

    print('Sending OTP Verification:');
    print('Email: ${widget.email}');
    print('OTP: ${_otpController.text}');


    final response = await http.post(
      Uri.parse(url),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "email": widget.email,
        "otp": _otpController.text,
        "password": widget.password, 
      }),
    );

    print('OTP Verification Status: ${response.statusCode}');
    print('OTP Verification Response Body: ${response.body}');
    print('OTP Verification Response Body: ${response.body}');

    setState(() {
      _isLoading = false;
    });

    final responseBody = jsonDecode(response.body);
    print('Parsed OTP Verification Response: $responseBody');

    if (response.statusCode == 200 || response.statusCode == 201) {
  // Adjust this condition based on your backend's exact response
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(responseBody['message'] ?? "User created successfully")),
  );


 Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => MultiScreenForm()),
      );
} else {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(responseBody['message'] ?? "Invalid OTP, please try again")),
  );
}

    } 
   catch (e) {
    print('OTP Verification Error: $e');
    setState(() {
      _isLoading = false;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Error verifying OTP: $e")),
    );
  }
}

  @override
  void dispose() {
    _timer?.cancel();
    _otpController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(30),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircleAvatar(
                radius: 60,
                backgroundColor: Color.fromARGB(255, 147, 182, 138),
                child: Icon(Icons.email_outlined, size: 50, color: Colors.black),
              ),
              const SizedBox(height: 36),
              const Text(
                'Verification Code',
                style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold, fontFamily: 'Poppins'),
              ),
              const SizedBox(height: 26),
              const Text(
                'An email OTP was sent to your email. Please check your email and enter the code below.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 36),

              TextField(
                controller: _otpController,
                textAlign: TextAlign.center,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: InputDecoration(
                  counterText: '',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),

              const SizedBox(height: 30),
              Text(
                _seconds > 0 ? 'Resend Code in $_seconds s' : 'Didn\'t receive the code?',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.grey),
              ),

             
             

              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _isLoading ? null : verifyOTP, // Disable button while loading
                child: _isLoading ? const CircularProgressIndicator() : const Text('Verify Code'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
