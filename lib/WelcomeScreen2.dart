import 'package:flutter/material.dart';
import 'package:ispani/Login.dart';
import 'package:timeline_tile/timeline_tile.dart';
import 'package:ispani/WelcomeScreen3.dart';

void main() {
  runApp(const Welcomescreen2());
}
class Welcomescreen2 extends StatefulWidget {
  const Welcomescreen2({super.key});

  @override
  State<Welcomescreen2> createState() => _Welcomescreen2State();
}

class _Welcomescreen2State extends State<Welcomescreen2> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
          child: Padding(padding: EdgeInsets.all(16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(height: 30,),
                Image.asset('assets/undraw_in-the-office_ma2b.png'),
                SizedBox(height: 26,),
                Text(
                  'A Nationwide FootPrint',
                  style: TextStyle(
                    fontWeight: FontWeight.w900,
                    fontSize: 35,
                    fontFamily: 'Poppins',
                  ),
                ),
                SizedBox(height: 16,),
                Text(
                  '1M+ jobs Available',
                  style: TextStyle(
                    fontWeight: FontWeight.w300,
                    fontSize: 15,
                  ),
                ),
                SizedBox(height: 56,),
                Text('We’re excited to help you take the next step in your career. Whether you’re looking for your dream job or the perfect candidate, you’ve come to the right place.Explore job opportunities, connect with'
                    'employers, and find your perfect match today. Lets build the future together!',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Poppins',
                    color: Colors.grey[700],
                  ),
                ),
                SizedBox(height: 180,),
                ElevatedButton(onPressed: () {
                  Navigator.push(context,MaterialPageRoute(builder: (context) => Welcomescreen3()),);
                },
                    style: ElevatedButton.styleFrom(
                      backgroundColor:Color.fromARGB(255, 147, 182, 138), // Change background color
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12), // Change border radius
                      ),
                      minimumSize: Size(double.infinity, 50), // Make it full width
                    ),
                    child: Text('Next',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                      ),
                    )),
                ElevatedButton(onPressed: () {
                  Navigator.push(context,MaterialPageRoute(builder: (context) => LoginScreen()),);
                },
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor: Colors.white, // Change background color
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12), // Change border radius
                      ),
                      minimumSize: Size(double.infinity, 50), // Make it full width
                    ),
                    child: Text('Skip',
                      style: TextStyle(
                          color: Colors.black,
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
