import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html; // For web storage fallback
import 'package:ispani/HomeScreen.dart';
import 'package:ispani/Login.dart'; // Assuming you have a HomeScreen

class MultiScreenForm extends StatefulWidget {
  final String? email;
  final String? password;
  final String? tempToken;

  const MultiScreenForm({
    Key? key,
    this.email,
    this.password,
    this.tempToken,
  }) : super(key: key);

  @override
  _MultiScreenFormState createState() => _MultiScreenFormState();
}

class _MultiScreenFormState extends State<MultiScreenForm> {
  int _currentStep = 0;
  final PageController _pageController = PageController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  int _selectedYear = 1;
  String _selectedNeed = "";
  String _selectedCommunication = "";
  List<String> _selectedJobs = [];
  List<String> _selectedHobbies = [];

  // Storage solutions
  final FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  bool _isWeb = false;
  bool _isLoading = false;

  // Controller for text fields
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _courseController = TextEditingController();
  final TextEditingController _qualificationController =
      TextEditingController();
  final TextEditingController _usernameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Check if we're running on web
    try {
      _isWeb = identical(0, 0.0);
    } catch (e) {
      _isWeb = false;
    }
  }

  // Method to safely store token
  Future<void> storeTokens(String accessToken, String refreshToken,
      String username, String email) async {
    if (_isWeb) {
      // Use localStorage for web
      html.window.localStorage['access_token'] = accessToken;
      html.window.localStorage['refresh_token'] = refreshToken;
      html.window.localStorage['username'] = username;
      html.window.localStorage['email'] = email;
    } else {
      // Use secure storage for mobile
      try {
        await _secureStorage.write(key: 'access_token', value: accessToken);
        await _secureStorage.write(key: 'refresh_token', value: refreshToken);
        await _secureStorage.write(key: 'username', value: username);
        await _secureStorage.write(key: 'email', value: email);
      } catch (e) {
        print("Secure storage error: $e");
        // Fallback to localStorage if secure storage fails
        html.window.localStorage['access_token'] = accessToken;
        html.window.localStorage['refresh_token'] = refreshToken;
        html.window.localStorage['username'] = username;
        html.window.localStorage['email'] = email;
      }
    }
  }

  // Method to safely get token
  Future<String> getToken() async {
    try {
      if (_isWeb) {
        return html.window.localStorage['access_token'] ?? '';
      } else {
        return await _secureStorage.read(key: 'access_token') ?? '';
      }
    } catch (e) {
      print("Error getting token: $e");
      // Fallback to localStorage if secure storage access fails
      return html.window.localStorage['access_token'] ?? '';
    }
  }

  // Method to safely get username
  Future<String> getUsername() async {
    try {
      if (_isWeb) {
        return html.window.localStorage['username'] ?? '';
      } else {
        return await _secureStorage.read(key: 'username') ?? '';
      }
    } catch (e) {
      print("Error getting username: $e");
      // Fallback to localStorage if secure storage access fails
      return html.window.localStorage['username'] ?? '';
    }
  }

  // Method to send form data to backend
  Future<void> _submitRegistration() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      final url = "http://127.0.0.1:8000/auth/complete-registration/";

      try {
        final response = await http.post(
          Uri.parse(url),
          headers: {
            "Content-Type": "application/json",
          },
          body: jsonEncode({
            "temp_token": widget.tempToken,
            "username": _usernameController.text,
            "year_of_study": _selectedYear,
            "course": _courseController.text,
            "hobbies": _selectedHobbies.join(', '),
            "piece_jobs": _selectedJobs.join(', '),
            "communication_preference": _selectedCommunication,
          }),
        );

        final responseData = jsonDecode(response.body);

        if (response.statusCode == 201) {
          // Check if the updated backend returns tokens
          if (responseData.containsKey('token') &&
              responseData.containsKey('user')) {
            // Store tokens and user info
            await storeTokens(
                responseData['token']['access'],
                responseData['token']['refresh'],
                responseData['user']['username'],
                responseData['user']['email']);

            // Registration successful and auto-login successful, navigate to home screen
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              content: Text("Registration successful! You are now logged in."),
              backgroundColor: Colors.green,
            ));

            // Navigate to the home screen
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => HomeScreen()),
            );
          } else {
            // Registration successful but no tokens returned (fallback)
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              content: Text("Registration successful! Please log in."),
              backgroundColor: Colors.green,
            ));

            // Navigate to the login screen
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => LoginScreen()),
            );
          }
        } else {
          // Handle error response
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("Error: ${responseData['error'] ?? 'Unknown error'}"),
            backgroundColor: Colors.red,
          ));
        }
      } catch (e) {
        // Handle network errors
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Network error: $e"),
          backgroundColor: Colors.red,
        ));
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _nextStep() {
    if (_formKey.currentState!.validate()) {
      if (_currentStep < 3) {
        setState(() {
          _currentStep++;
        });
        _pageController.nextPage(
            duration: Duration(milliseconds: 300), curve: Curves.easeInOut);
      } else {
        // Submit the form data to the backend when on the last step
        _submitRegistration();
      }
    }
  }

  void _prevStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
          duration: Duration(milliseconds: 300), curve: Curves.easeInOut);
    }
  }

  Widget _buildTextField(
      String label, String hint, TextEditingController controller) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: OutlineInputBorder(),
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return "This field is required";
        }
        return null;
      },
    );
  }

  Widget _buildRadioList(
      List<String> options, String selectedValue, Function(String?) onChanged) {
    return Column(
      children: options.map((option) {
        return RadioListTile(
          title: Text(option),
          value: option,
          groupValue: selectedValue,
          onChanged: onChanged,
        );
      }).toList(),
    );
  }

  Widget _buildCheckboxList(List<String> options, List<String> selectedValues) {
    return Column(
      children: options.map((option) {
        return CheckboxListTile(
          title: Text(option),
          value: selectedValues.contains(option),
          onChanged: (bool? value) {
            setState(() {
              if (value == true) {
                selectedValues.add(option);
              } else {
                selectedValues.remove(option);
              }
            });
          },
        );
      }).toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
          backgroundColor: Colors.white, title: Text("Registration Form")),
      body: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            LinearProgressIndicator(
              value: (_currentStep + 1) / 4,
              color: Color.fromARGB(255, 147, 182, 138),
              backgroundColor: Colors.grey[300],
            ),
            SizedBox(height: 10),
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: NeverScrollableScrollPhysics(),
                children: [
                  _buildScreen1(),
                  _buildScreen2(),
                  _buildScreen3(),
                  _buildScreen4(),
                ],
              ),
            ),
            SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                4,
                (index) => Row(
                  children: [
                    CircleAvatar(
                      radius: 5,
                      backgroundColor: _currentStep >= index
                          ? Color.fromARGB(255, 147, 182, 138)
                          : Colors.grey[700],
                    ),
                    if (index < 3)
                      Container(
                        width: 20,
                        height: 2,
                        color: _currentStep > index
                            ? Color.fromARGB(255, 147, 182, 138)
                            : Colors.grey,
                      ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 60),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                if (_currentStep > 0)
                  ElevatedButton(
                    onPressed: _isLoading ? null : _prevStep,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color.fromARGB(255, 147, 182, 138),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      "Back",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                ElevatedButton(
                  onPressed: _isLoading ? null : _nextStep,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color.fromARGB(255, 147, 182, 138),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text(
                          _currentStep == 3 ? "Submit" : "Next",
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                ),
              ],
            ),
            SizedBox(height: 50),
          ],
        ),
      ),
    );
  }

  Widget _buildScreen1() {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Basic Information",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 36),
          _buildTextField("Username", "Choose a username", _usernameController),
          SizedBox(height: 16),
          _buildTextField("Course", "Enter your Course", _courseController),
        ],
      ),
    );
  }

  Widget _buildScreen2() {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Academic & Work Details",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text("Year of Study"),
          _buildRadioList(["1", "2", "3"], _selectedYear.toString(), (val) {
            setState(() {
              _selectedYear = int.parse(val!);
            });
          }),
          SizedBox(height: 16),
          Text("What piece jobs would you do?"),
          _buildCheckboxList(
              ["Tutoring", "Selling stuff", "Delivering on campus"],
              _selectedJobs),
        ],
      ),
    );
  }

  Widget _buildScreen3() {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Hobbies & Needs",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          _buildCheckboxList(["Chess", "Soccer"], _selectedHobbies),
        ],
      ),
    );
  }

  Widget _buildScreen4() {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Communication Preference",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          _buildRadioList(["Whatsapp", "Email", "Call"], _selectedCommunication,
              (val) {
            setState(() {
              _selectedCommunication = val!;
            });
          }),
        ],
      ),
    );
  }
}
