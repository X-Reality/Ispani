import 'package:flutter/material.dart';
import 'StudentDetailScreen.dart';

class StudentBookingScreen extends StatelessWidget {
  const StudentBookingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final bookings = [
      {'name': 'Alice Smith', 'status': 'Pending', 'date': 'Apr 28, 2025'},
      {'name': 'John Doe', 'status': 'Confirmed', 'date': 'Apr 29, 2025'},
      {'name': 'Sophia Brown', 'status': 'Completed', 'date': 'Apr 27, 2025'},
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Bookings'),
      ),
      body: ListView.separated(
        itemCount: bookings.length,
        separatorBuilder: (_, __) => const Divider(),
        itemBuilder: (context, index) {
          final booking = bookings[index];
          return ListTile(
            leading: CircleAvatar(
              child: Text(booking['name']![0]),
            ),
            title: Text(booking['name']!),
            subtitle: Text(booking['status']!),
            trailing: Text(booking['date']!),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => StudentDetailScreen(studentName: booking['name']!, status: booking['status']!)),
              );
            },
          );
        },
      ),
    );
  }
}
