import 'package:flutter/material.dart';

class StudentDetailScreen extends StatelessWidget {
  final String studentName;
  final String status;

  const StudentDetailScreen(
      {super.key, required this.studentName, required this.status});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('$studentName Details'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Name: $studentName', style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 10),
            Text('Status: $status', style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 10),
            const Text('Lesson Topic: Mobile App Development',
                style: TextStyle(fontSize: 16)),
            const SizedBox(height: 10),
            const Text('Scheduled Time: Apr 29, 2025, 3 PM',
                style: TextStyle(fontSize: 16)),
            const Spacer(),
            ElevatedButton.icon(
              onPressed: () {
                // You can add navigation to start lesson, send message, etc.
              },
              icon: const Icon(Icons.message),
              label: const Text('Message Student'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            )
          ],
        ),
      ),
    );
  }
}
