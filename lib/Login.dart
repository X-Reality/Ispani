import 'package:flutter/material.dart';
import 'package:ispani/Forgotpassword.dart';
import 'package:ispani/HomeScreen.dart';
import 'package:ispani/SignUp.dart';
import 'package:ispani/TutorHomeScreen.dart'; // Add this import

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: LoginScreen(),
  ));
}

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

  bool _isLoading = false;

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _handleLogin(Widget screen, String message) async {
    if (_formKey.currentState!.validate()) {
      _showSnackbar(message);
      setState(() {
        _isLoading = true;
      });

      await Future.delayed(Duration(seconds: 1, milliseconds: 500));

      setState(() {
        _isLoading = false;
      });

      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => screen),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          SingleChildScrollView(
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
                ),

                // Login Form
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
                        children: [
                          Text(
                            'Welcome Back',
                            style: TextStyle(fontSize: 35, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 10),
                          Text('Please enter your credentials to continue.'),
                          SizedBox(height: 20),

                          // Email Field
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
                              if (value == null || value.isEmpty) {
                                return "Email is required";
                              } else if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(value)) {
                                return "Enter a valid email";
                              }
                              return null;
                            },
                          ),
                          SizedBox(height: 20),

                          // Password Field
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
                              if (value == null || value.isEmpty) {
                                return "Password is required";
                              } else if (value.length < 6) {
                                return "Password must be at least 6 characters";
                              }
                              return null;
                            },
                          ),
                          SizedBox(height: 10),

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Checkbox(
                                    value: isChecked,
                                    onChanged: (value) {
                                      setState(() {
                                        isChecked = value!;
                                      });
                                    },
                                  ),
                                  Text("Remember Me"),
                                ],
                              ),
                              InkWell(
                                onTap: () {
                                  Navigator.push(context,
                                      MaterialPageRoute(builder: (context) => Forgotpassword()));
                                },
                                child: Text(
                                  'Forgot Password?',
                                  style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // Login Button with GestureDetector
                          GestureDetector(
                            onTap: () => _handleLogin(HomeScreen(), 'Logging in...'),
                            onDoubleTap: () => _handleLogin(TutorHomeScreen(), 'Logging in as tutor...'),
                            child: ElevatedButton(
                              onPressed: null, // Disabled
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Color.fromARGB(255, 147, 182, 138),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                minimumSize: Size(double.infinity, 50),
                              ),
                              child: Text(
                                'Login',
                                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
                              ),
                            ),
                          ),
                          SizedBox(height: 20),

                          // Sign up
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text("Don't have an account? "),
                              InkWell(
                                onTap: () {
                                  Navigator.push(context,
                                      MaterialPageRoute(builder: (context) => SignupScreen()));
                                },
                                child: Text('Sign up',
                                    style: TextStyle(color: Color.fromARGB(255, 147, 182, 138))),
                              ),
                            ],
                          ),
                          SizedBox(height: 30),

                          // OR Divider
                          Stack(
                            children: [
                              Divider(),
                              Center(
                                child: Container(
                                  width: 60,
                                  color: Colors.white,
                                  child: Text('OR', textAlign: TextAlign.center),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 36),

                          // Facebook Login
                          ElevatedButton(
                            onPressed: () {},
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              side: BorderSide(color: Colors.grey),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              minimumSize: Size(double.infinity, 50),
                              alignment: Alignment.centerLeft,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.facebook_outlined, color: Colors.black),
                                SizedBox(width: 10),
                                Text("Sign in with Facebook", style: TextStyle(color: Colors.black)),
                              ],
                            ),
                          ),
                          SizedBox(height: 16),

                          // Google Login
                          ElevatedButton(
                            onPressed: () {},
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              side: BorderSide(color: Colors.grey),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              minimumSize: Size(double.infinity, 50),
                              alignment: Alignment.centerLeft,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.face, color: Colors.black),
                                SizedBox(width: 10),
                                Text("Sign in with Google", style: TextStyle(color: Colors.black)),
                              ],
                            ),
                          ),
                          SizedBox(height: 16),

                          // Apple Login
                          ElevatedButton(
                            onPressed: () {},
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              side: BorderSide(color: Colors.grey),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              minimumSize: Size(double.infinity, 50),
                              alignment: Alignment.centerLeft,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.apple, color: Colors.black),
                                SizedBox(width: 10),
                                Text("Sign in with Apple", style: TextStyle(color: Colors.black)),
                              ],
                            ),
                          ),
                          SizedBox(height: 30),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Spinner Overlay
          if (_isLoading)
            Container(
              color: Colors.black38,
              child: Center(child: CircularProgressIndicator()),
            ),
        ],
      ),
    );
  }
}
