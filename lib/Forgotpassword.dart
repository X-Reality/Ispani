import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: Forgotpassword(),
  ));
}
class Forgotpassword extends StatefulWidget {
  const Forgotpassword({super.key});

  @override
  State<Forgotpassword> createState() => _ForgotpasswordState();
}

class _ForgotpasswordState extends State<Forgotpassword> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(padding: EdgeInsets.all(30),
        child: Column(
          mainAxisSize: MainAxisSize.min,
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
              'Forgot Password',
              style: TextStyle(
                fontSize: 30,
                fontWeight: FontWeight.bold,
                fontFamily: 'Poppins',
              ),
            ),
            SizedBox(height: 30,),
            TextField(
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
            SizedBox(height: 30,),
            ElevatedButton(
              onPressed: (){}, // Validate form on click
              style: ElevatedButton.styleFrom(
                backgroundColor:Color.fromARGB(255, 147, 182, 138),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                minimumSize: Size(double.infinity, 50),
              ),
              child: Text(
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
        )

      ),
    );
  }
}
