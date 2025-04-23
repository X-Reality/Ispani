import 'package:flutter/material.dart';
import 'package:ispani/Login.dart';

void main() {
  runApp(const Welcomescreen3());
}

class Welcomescreen3 extends StatefulWidget {
  const Welcomescreen3({super.key});

  @override
  State<Welcomescreen3> createState() => _Welcomescreen3State();
}

class _Welcomescreen3State extends State<Welcomescreen3> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
          child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              height: 30,
            ),
            Image.asset('assets/undraw_connected-world_anke.png'),
            SizedBox(
              height: 26,
            ),
            Text(
              'Connect with US',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 35,
                fontFamily: 'Poppins',
              ),
            ),
            SizedBox(
              height: 16,
            ),
            Text(
              '500K+ Members',
              style: TextStyle(
                fontWeight: FontWeight.w300,
                fontSize: 15,
              ),
            ),
            SizedBox(
              height: 56,
            ),
            Text(
              'We’re excited to help you take the next step in your career. Whether you’re looking for your dream job or the perfect candidate, you’ve come to the right place.Explore job opportunities, connect with'
              'employers, and find your perfect match today. Lets build the future together!',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Poppins',
                color: Colors.grey[700],
              ),
            ),
            SizedBox(
              height: 180,
            ),
            ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => LoginScreen()),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color.fromARGB(
                      255, 147, 182, 138), // Change background color
                  shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(12), // Change border radius
                  ),
                  minimumSize: Size(double.infinity, 50), // Make it full width
                ),
                child: Text(
                  'Login',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                )),
          ],
        ),
      )),
    );
  }
}
