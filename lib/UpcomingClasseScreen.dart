import 'package:flutter/material.dart';


class UpcomingClassesScreen extends StatelessWidget {
  final List<Map<String, String>> classes = [
    {
      'name': 'Sophia Lee',
      'type': 'High School Learner',
      'date': 'May 14',
      'time': '11:00 AM',
      'subject': 'Biology',
    },
    {
      'name': 'Oliver Brown',
      'type': 'Student',
      'date': 'May 14',
      'time': '3:00 PM',
      'subject': 'English Literature',
    },
    // Add more classes
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Upcoming Classes"),
        centerTitle: true,
        backgroundColor: Colors.green.shade700,
      ),
      body: ListView.builder(
        itemCount: classes.length,
        itemBuilder: (context, index) {
          final classData = classes[index];
          return Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 4,
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: ListTile(
              leading: classData['type'] == 'Student'
                  ? Icon(Icons.school, color: Colors.green.shade700)
                  : Icon(Icons.ice_skating_outlined, color: Colors.green.shade700),
              title: Text(classData['name']!, style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${classData['subject']} - ${classData['date']} at ${classData['time']}'),
              trailing: Icon(Icons.chevron_right),
              onTap: () {
                // Handle tap
              },
            ),
          );
        },
      ),
    );
  }
}
