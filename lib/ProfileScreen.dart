import 'package:flutter/material.dart';

class ProfileScreen extends StatefulWidget {
  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  List<Map<String, dynamic>> experiences = [];
  List<String> skills = [];
  List<String> services = [];
  String about = '';
  String activity = '';

  final TextEditingController skillController = TextEditingController();
  final TextEditingController serviceController = TextEditingController();
  final TextEditingController aboutController = TextEditingController();

  void _addSkill() {
    if (skillController.text.isNotEmpty) {
      setState(() {
        skills.add(skillController.text);
        skillController.clear();
      });
    }
  }

  void _addService() {
    if (serviceController.text.isNotEmpty) {
      setState(() {
        services.add(serviceController.text);
        serviceController.clear();
      });
    }
  }

  void _addExperience() {
    TextEditingController companyController = TextEditingController();
    TextEditingController startDateController = TextEditingController();
    TextEditingController endDateController = TextEditingController();
    bool currentlyWorking = false;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text('Add Experience'),
              content: SingleChildScrollView(
                child: Column(
                  children: [
                    TextField(
                      controller: companyController,
                      decoration: InputDecoration(hintText: 'Company Name'),
                    ),
                    TextField(
                      controller: startDateController,
                      decoration: InputDecoration(hintText: 'Start Date'),
                    ),
                    TextField(
                      controller: endDateController,
                      decoration: InputDecoration(hintText: 'End Date'),
                      enabled: !currentlyWorking,
                    ),
                    CheckboxListTile(
                      title: Text('Currently Working Here'),
                      value: currentlyWorking,
                      onChanged: (value) {
                        setState(() {
                          currentlyWorking = value!;
                          if (currentlyWorking) {
                            endDateController.clear();
                          }
                        });
                      },
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    setState(() {
                      experiences.add({
                        'company': companyController.text,
                        'startDate': startDateController.text,
                        'endDate': currentlyWorking ? 'Present' : endDateController.text,
                      });
                    });
                    Navigator.pop(context);
                  },
                  child: Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _editAbout() {
    aboutController.text = about;
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Edit About'),
          content: TextField(
            controller: aboutController,
            maxLines: 5,
            decoration: InputDecoration(hintText: 'Enter about section'),
          ),
          actions: [
            TextButton(
              onPressed: () {
                setState(() => about = aboutController.text);
                Navigator.pop(context);
              },
              child: Text('Save'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Profile'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  height: 150,
                  width: double.infinity,
                  color: Colors.blueGrey,
                ),
                Positioned(
                  top: 80,
                  left: MediaQuery.of(context).size.width / 2 - 80,
                  child: CircleAvatar(
                    radius: 60,
                    backgroundImage: AssetImage('assets/profile.jpg'),
                  ),
                ),
              ],
            ),
            SizedBox(height: 60),
            Text(
              'Kitso Sejake',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            Text('Software Engineer | UI/UX Designer | Full Stack | Flutter | NodeJS'),
            Divider(height: 30),
            _fullWidthContainer(
              ListTile(
                title: Text('About'),
                subtitle: Text(about.isEmpty ? 'No about section added' : about),
                trailing: IconButton(
                  icon: Icon(Icons.edit),
                  onPressed: _editAbout,
                ),
              ),
            ),
            _fullWidthContainer(_experienceSection()),
            _fullWidthContainer(_skillsSection()),
            _fullWidthContainer(_servicesSection()),
            _fullWidthContainer(_activitySection()),
          ],
        ),
      ),
    );
  }

  Widget _fullWidthContainer(Widget child) {
    return Container(
      width: double.infinity,
      child: child,
    );
  }

  Widget _experienceSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ListTile(
          title: Text('Experience'),
          trailing: IconButton(
            icon: Icon(Icons.add),
            onPressed: _addExperience,
          ),
        ),
        ...experiences.map(
              (exp) => ListTile(
            title: Text(exp['company'] ?? ''),
            subtitle: Text('${exp['startDate']} - ${exp['endDate']}'),
          ),
        ),
      ],
    );
  }

  Widget _skillsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Skills', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Wrap(
          spacing: 8,
          children: skills.map((skill) => Chip(label: Text(skill))).toList(),
        ),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: skillController,
                decoration: InputDecoration(hintText: 'Add Skill'),
              ),
            ),
            IconButton(
              icon: Icon(Icons.add),
              onPressed: _addSkill,
            ),
          ],
        ),
      ],
    );
  }

  Widget _servicesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ListTile(
          title: Text('Services'),
          trailing: IconButton(
            icon: Icon(Icons.add),
            onPressed: _addService,
          ),
        ),
        Wrap(
          spacing: 8,
          children: services.map((service) => Chip(label: Text(service))).toList(),
        ),
      ],
    );
  }

  Widget _activitySection() {
    return ListTile(
      title: Text('Activity'),
      subtitle: Text(activity.isEmpty ? 'No activity recorded yet' : activity),
    );
  }
}
