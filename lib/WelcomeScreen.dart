import 'package:flutter/material.dart';
import 'package:ispani/WelcomeScreen2.dart';

void main() {
  runApp(const WelcomeScreen());
}

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(padding: EdgeInsets.all(16),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.asset('assets/undraw_explore_kfv3.png'),
                  SizedBox(height: 56,),
                  Text(
                    'Start a Career today',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 35,
                    ),
                  ),
                  SizedBox(height: 56,),
                  Text('We’re excited to help you take the next step in your career. Whether you’re looking for your dream job or the perfect candidate, you’ve come to the right place.Explore job opportunities, connect with'
                      'employers, and find your perfect match today. Lets build the future together!',
                       textAlign: TextAlign.center,
                       style: TextStyle(

                         color: Colors.grey[700],
                       ),
                  ),
                  SizedBox(height: 250,),
                  ElevatedButton(onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => Welcomescreen2()),
                    );
                  },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color.fromARGB(255, 147, 182, 138), // Change background color
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12), // Change border radius
                        ),
                        minimumSize: Size(double.infinity, 50), // Make it full width
                      ),
                      child: Text('Get Started',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold
                        ),
                      ))

                ],
              ),

            )

      ),
    );
  }
}
