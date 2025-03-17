import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html; // For web storage fallback

void main() {
  runApp(MaterialApp(
    home: MultiScreenForm(),
  ));
}

class MultiScreenForm extends StatefulWidget {
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

  // Controller for text fields
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _courseController = TextEditingController();
  final TextEditingController _qualificationController = TextEditingController();

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
  Future<void> storeTokens(String token, String userId) async {
    if (_isWeb) {
      // Use localStorage for web
      html.window.localStorage['jwt_token'] = token;
      html.window.localStorage['user_id'] = userId;
    } else {
      // Use secure storage for mobile
      try {
        await _secureStorage.write(key: 'jwt_token', value: token);
        await _secureStorage.write(key: 'user_id', value: userId);
      } catch (e) {
        print("Secure storage error: $e");
        // Fallback to localStorage if secure storage fails
        html.window.localStorage['jwt_token'] = token;
        html.window.localStorage['user_id'] = userId;
      }
    }
  }

  // Method to safely get token
  Future<String> getToken() async {
    try {
      if (_isWeb) {
        return html.window.localStorage['jwt_token'] ?? '';
      } else {
        return await _secureStorage.read(key: 'jwt_token') ?? '';
      }
    } catch (e) {
      print("Error getting token: $e");
      // Fallback to localStorage if secure storage access fails
      return html.window.localStorage['jwt_token'] ?? '';
    }
  }

  // Method to safely get user ID
  Future<String> getUserId() async {
    try {
      if (_isWeb) {
        return html.window.localStorage['user_id'] ?? '';
      } else {
        return await _secureStorage.read(key: 'user_id') ?? '';
      }
    } catch (e) {
      print("Error getting user ID: $e");
      // Fallback to localStorage if secure storage access fails
      return html.window.localStorage['user_id'] ?? '';
    }
  }

  // Method to handle the successful OTP verification and token storage
  Future<void> handleSuccessfulAuth(Map<String, dynamic> responseData) async {
    if (responseData.containsKey('access') && responseData.containsKey('user')) {
      final token = responseData['access'];
      final userId = responseData['user']['id'].toString();
      
      await storeTokens(token, userId);
    }
  }

  // Method to send form data to backend
  Future<void> _submitRegistration() async {
    if (_formKey.currentState!.validate()) {
      final url = "http://127.0.0.1:8000/registration/";

      try {
        final response = await http.post(
          Uri.parse(url),
          headers: {
            "Content-Type": "application/json",
          },
          body: jsonEncode({
            "name": _nameController.text, 
            "course": _courseController.text,
            "qualification": _qualificationController.text,
            "year_of_study": _selectedYear, // Ensure this is an integer
            "piece_jobs": _selectedJobs, // Ensure this is a list of strings
            "hobbies": _selectedHobbies, // Ensure this is a list of strings
            "communication_preference": _selectedCommunication, // Ensure this is a string
          }),
        );

        final responseData = jsonDecode(response.body);

        if (response.statusCode == 201 || response.statusCode == 200) {
          // Handle successful response
          if (responseData.containsKey('access') && responseData.containsKey('user')) {
            final token = responseData['access'];
            final userId = responseData['user']['id'].toString();
            await storeTokens(token, userId);
          }
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(responseData['message'] ?? "Registration successful!"),
            backgroundColor: Colors.green,
          ));
        } else {
          // Handle error response
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("Error: ${responseData['detail'] ?? 'Unknown error'}"),
          ));
        }

      } catch (e) {
        // Handle network errors
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Network error: $e"),
        ));
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

  Widget _buildTextField(String label, String hint, TextEditingController controller) {
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

  Widget _buildRadioList(List<String> options, String selectedValue, Function(String?) onChanged) {
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
      appBar: AppBar(backgroundColor: Colors.white, title: Text("Registration Form")),
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
                    onPressed: _prevStep,
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
                  onPressed: _nextStep,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color.fromARGB(255, 147, 182, 138),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
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
          _buildTextField("Name", "Enter your name", _nameController),
          SizedBox(height: 16),
          _buildTextField("Course", "Enter your Course", _courseController),
          SizedBox(height: 16),
          _buildTextField("Qualification", "Enter your Qualification", _qualificationController),
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
          _buildCheckboxList(["Tutoring", "Selling stuff", "Delivering on campus"], _selectedJobs),
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
          Text("Hobbies & Needs", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
          Text("Communication Preference", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          _buildRadioList(["Whatsapp", "Email", "Call"], _selectedCommunication, (val) {
            setState(() {
              _selectedCommunication = val!;
            });
          }),
        ],
      ),
    );
  }
}