import 'dart:async';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';  // <-- Add this package

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: OtpScreen(email: "user@example.com"), // Example email passed here
  ));
}

class OtpScreen extends StatefulWidget {
  final String? email;
  const OtpScreen({super.key, this.email});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  int _seconds = 60; // 1-minute countdown
  Timer? _timer;

  // Controllers for each OTP digit input
  final List<TextEditingController> _otpControllers =
  List.generate(5, (_) => TextEditingController());

  @override
  void initState() {
    super.initState();
    startTimer();
  }

  void startTimer() {
    _timer?.cancel();
    _seconds = 60;
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_seconds > 0) {
        setState(() {
          _seconds--;
        });
      } else {
        _timer?.cancel();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (var c in _otpControllers) {
      c.dispose();
    }
    super.dispose();
  }

  // Combine OTP digits into one string
  String getCombinedOtp() {
    return _otpControllers.map((c) => c.text).join();
  }

  // Simple OTP validation (5 digits)
  bool isOtpValid(String otp) {
    return otp.length == 5 && RegExp(r'^\d{5}$').hasMatch(otp);
  }

  // On Verify pressed
  Future<void> verifyOtp() async {
    final otp = getCombinedOtp();
    if (!isOtpValid(otp)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Please enter a valid 5-digit OTP.")),
      );
      return;
    }

    if (widget.email == null || widget.email!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Email is missing, cannot proceed.")),
      );
      return;
    }

    // Construct URL to React website, pass email as query param
    final Uri url = Uri.parse(
      "https://ispani.net/signup?email=${Uri.encodeComponent(widget.email!)}",
    );

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Could not open the signup website.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(30),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircleAvatar(
                  radius: 60,
                  backgroundColor: Color.fromARGB(255, 147, 182, 138),
                  child: Icon(Icons.email_outlined, size: 50, color: Colors.black),
                ),
                SizedBox(height: 36),
                Text(
                  'Verification Code',
                  style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'Poppins',
                  ),
                ),
                SizedBox(height: 26),
                Text(
                  'An email OTP was sent to ${widget.email ?? "your email"}. Please enter the code below.',
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 36),

                // OTP input fields
                Wrap(
                  spacing: 10,
                  children: List.generate(5, (index) {
                    return SizedBox(
                      width: 60,
                      child: TextField(
                        controller: _otpControllers[index],
                        textAlign: TextAlign.center,
                        keyboardType: TextInputType.number,
                        maxLength: 1,
                        onChanged: (value) {
                          if (value.length == 1 && index < 4) {
                            FocusScope.of(context).nextFocus();
                          } else if (value.isEmpty && index > 0) {
                            FocusScope.of(context).previousFocus();
                          }
                        },
                        decoration: InputDecoration(
                          counterText: '',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                      ),
                    );
                  }),
                ),

                SizedBox(height: 30),
                Text(
                  _seconds > 0 ? 'Resend Code in $_seconds s' : 'Didn\'t receive the code?',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey,
                  ),
                ),
                SizedBox(height: 100),
                ElevatedButton(
                  onPressed: _seconds == 0
                      ? () {
                    startTimer();
                  }
                      : null,
                  style: ElevatedButton.styleFrom(
                    elevation: 0,
                    backgroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    minimumSize: Size(double.infinity, 50),
                  ),
                  child: Text(
                    'Resend Code',
                    style: TextStyle(
                      color: _seconds == 0 ? Colors.black : Colors.grey,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),

                SizedBox(height: 16),
                ElevatedButton(
                  onPressed: verifyOtp,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color.fromARGB(255, 147, 182, 138),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    minimumSize: Size(double.infinity, 50),
                  ),
                  child: Text(
                    'Verify Code',
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
      ),
    );
  }
}
