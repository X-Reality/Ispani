import 'dart:async';
import 'package:flutter/material.dart';
import 'package:ispani/HomeScreen.dart';
import 'package:ispani/Register.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: OtpScreen(),
  ));
}

class OtpScreen extends StatefulWidget {
  const OtpScreen({super.key});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  int _seconds = 60; // 1-minute countdown
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    startTimer(); // Start the timer automatically
  }

  void startTimer() {
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_seconds > 0) {
        setState(() {
          _seconds--;
        });
      } else {
        _timer!.cancel(); // Stop timer when it reaches 0
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel(); // Cleanup when widget is removed
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: EdgeInsets.all(30),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 60, // Increased size
                    backgroundColor: Color.fromARGB(255, 147, 182, 138),
                    child: Icon(
                      Icons.email_outlined,
                      size: 50,
                      color: Colors.black,
                    ),
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
                    'An email OTP was sent to your email. Please check your email and enter the code below.',
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 36),

                  // OTP Fields
                  Wrap(
                    spacing: 10, // Adds spacing between input boxes
                    children: List.generate(
                      5,
                          (index) => SizedBox(
                        width: 60,
                        child: TextField(
                          textAlign: TextAlign.center,
                          keyboardType: TextInputType.number,
                          maxLength: 1,
                          decoration: InputDecoration(
                            counterText: '',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            filled: true,
                            fillColor: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),

                  SizedBox(height: 30),
                  Text(
                    _seconds > 0 ? 'Resend Code in $_seconds s' : 'Didn\'t receive the code?',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.grey),
                  ),

                  SizedBox(height: 100),
                  ElevatedButton(
                    onPressed: _seconds == 0
                        ? () {
                      setState(() {
                        _seconds = 60; // Reset the timer
                      });
                      startTimer();
                    }
                        : null, // Disable button while timer is running
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
                        color: _seconds == 0 ? Colors.black : Colors.grey, // Disable color if timer is running
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),

                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(context, MaterialPageRoute(builder: (context) => MultiScreenForm()));
                    },
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
          ],
        ),
      ),
    );
  }
}
