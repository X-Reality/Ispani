import 'package:flutter/material.dart';
import 'package:ispani/HomeScreen.dart';

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

  // Controller for text fields
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _courseController = TextEditingController();
  final TextEditingController _qualificationController = TextEditingController();

  void _nextStep() {
    if (_formKey.currentState!.validate()) {
      if (_currentStep < 3) {
        setState(() {
          _currentStep++;
        });
        _pageController.nextPage(
            duration: Duration(milliseconds: 300), curve: Curves.easeInOut);
      } else {
        // Navigate to Home Screen
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => HomeScreen()),
        );
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
      appBar: AppBar(backgroundColor: Colors.white, title: Text("Registration  Form")),
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
          _buildTextField("Username", "Enter your Username", _nameController),
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
         _buildCheckboxList(["Tutoring", "Selling stuff", "Delivering on campus","Hairstyling","Phone Repair", "CAD and 3D Modeling"], _selectedJobs),
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
          _buildCheckboxList(["Chess", "Soccer","Gym, Jogging","Singing,Church,Dancing,Content Creating","Other"], _selectedHobbies),
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
          Text("Preferences", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          _buildRadioList(["WhatsApp", "Email","Class","SMS"], _selectedCommunication, (val) {
            setState(() {
              _selectedCommunication = val!;
            });
          }),
        ],
      ),
    );
  }
}
