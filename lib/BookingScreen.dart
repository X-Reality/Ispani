import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:ispani/BookingDetailScreen.dart';

class StudentBookingsScreen extends StatelessWidget {
  final List<Map<String, String>> bookings = [
    {
      'name': 'Emily Johnson',
      'type': 'Student',
      'date': 'May 15',
      'time': '10:00 AM',
      'subject': 'Math',
      'location': 'Room 101',
      'notes': 'Needs help with algebra.'
    },
    {
      'name': 'Liam Smith',
      'type': 'High School Learner',
      'date': 'May 16',
      'time': '12:30 PM',
      'subject': 'Physics',
      'location': 'Lab 3',
      'notes': 'Review exam prep.'
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("All Bookings")),
      body: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: bookings.length,
        itemBuilder: (context, index) {
          final booking = bookings[index];
          return InkWell(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => BookingDetailScreen(booking: booking),
                ),
              );
            },
            child: Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              elevation: 5,
              margin: EdgeInsets.symmetric(vertical: 10),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 24,
                          backgroundColor: Colors.green.shade700.withOpacity(0.1),
                          child: Icon(
                            booking['type'] == 'Student'
                                ? CupertinoIcons.profile_circled
                                : CupertinoIcons.hare,
                            color: Colors.green.shade700,
                          ),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                booking['name']!,
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              SizedBox(height: 4),
                              Text(
                                booking['type']!,
                                style: TextStyle(color: Colors.grey.shade600),
                              ),
                            ],
                          ),
                        ),
                        Icon(Icons.chevron_right, color: Colors.grey),
                      ],
                    ),
                    SizedBox(height: 16),
                    Row(
                      children: [
                        Icon(Icons.book, size: 16, color: Colors.grey.shade600),
                        SizedBox(width: 6),
                        Text(booking['subject']!, style: TextStyle(color: Colors.black87)),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(Icons.calendar_today, size: 16, color: Colors.grey.shade600),
                        SizedBox(width: 6),
                        Text("${booking['date']} at ${booking['time']}", style: TextStyle(color: Colors.black87)),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(Icons.location_on, size: 16, color: Colors.grey.shade600),
                        SizedBox(width: 6),
                        Text(booking['location'] ?? 'N/A', style: TextStyle(color: Colors.black87)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
