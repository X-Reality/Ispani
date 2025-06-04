import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:ispani/BookingCalendarScreen.dart';

class StudentBookingCalendarScreen extends StatefulWidget {
  @override
  _StudentBookingCalendarScreenState createState() => _StudentBookingCalendarScreenState();
}

class _StudentBookingCalendarScreenState extends State<StudentBookingCalendarScreen> {
  DateTime selectedDate = DateTime.now();

  final List<Map<String, dynamic>> bookings = [
    {
      'name': 'Emily Johnson',
      'type': 'Student',
      'subject': 'Math',
      'start': TimeOfDay(hour: 9, minute: 0),
      'end': TimeOfDay(hour: 10, minute: 0),
      'date': DateTime.now(),
      'location': 'Room A',
      'notes': 'Algebra topics'
    },
    {
      'name': 'Liam Smith',
      'type': 'High School Learner',
      'subject': 'Physics',
      'start': TimeOfDay(hour: 12, minute: 30),
      'end': TimeOfDay(hour: 13, minute: 30),
      'date': DateTime.now(),
      'location': 'Room B',
      'notes': 'Newtons Laws'
    },
    {
      'name': 'Liam Smith',
      'type': 'High School Learner',
      'subject': 'Physics',
      'start': TimeOfDay(hour: 08, minute: 0),
      'end': TimeOfDay(hour: 09, minute: 0),
      'date': DateTime.now(),
      'location': 'Room B',
      'notes': 'Newtons Laws'
    },
  ];

  List<DateTime> getNext14Days() {
    return List.generate(14, (index) => DateTime.now().add(Duration(days: index)));
  }

  @override
  Widget build(BuildContext context) {
    final hours = List.generate(13, (index) => 8 + index); // 8 AM to 8 PM

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: Text("Student Bookings"),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: EdgeInsets.all(16),child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('May 2024',style: TextStyle(fontSize: 36,fontWeight: FontWeight.bold),),

                ],
              ),
              Row(
                  children: [
                    IconButton(onPressed: (){}, icon: Icon(Icons.search)),
                    IconButton(onPressed: (){
                      Navigator.push(context,
                          MaterialPageRoute(builder: (context) => BookingCalendarScreen()));
                    }, icon: Icon(Icons.sort))
                  ]

              )
            ],
          ) ,),
          Container(
            height: 80,
            padding: EdgeInsets.symmetric(horizontal: 8),
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: getNext14Days().map((date) {
                bool isSelected = DateFormat('yyyy-MM-dd').format(date) == DateFormat('yyyy-MM-dd').format(selectedDate);
                return GestureDetector(
                  onTap: () => setState(() => selectedDate = date),
                  child: Container(
                    width: 80,
                    margin: EdgeInsets.symmetric(horizontal: 6, vertical: 12),
                    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected ? Colors.green.shade700 : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(DateFormat('d').format(date), style: TextStyle(fontSize: 16, color: isSelected ? Colors.white : Colors.black)),
                        SizedBox(height: 4),
                        Text(DateFormat('E').format(date), style: TextStyle(fontSize: 14, color: isSelected ? Colors.white : Colors.black)),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          SizedBox(height: 16,),
          Expanded(
            child: SingleChildScrollView(
              child: SizedBox(
                height: 13 * 100.0, // 13 hours from 8 to 20
                child: Stack(
                  children: [
                    // Timeline hours
                    for (int i = 0; i < 13; i++)
                      Positioned(
                        top: i * 100.0,
                        left: 16,
                        child: Text(
                          "${(8 + i).toString().padLeft(2, '0')}:00",
                          style: TextStyle(color: Colors.grey),
                        ),
                      ),

                    // Horizontal divider lines
                    for (int i = 0; i < 13; i++)
                      Positioned(
                        top: i * 100.0 + 25,
                        left: 60,
                        right: 0,
                        child: Divider(color: Colors.grey.shade300),
                      ),

                    // Bookings
                    ...bookings.where((booking) =>
                    DateFormat('yyyy-MM-dd').format(booking['date']) ==
                        DateFormat('yyyy-MM-dd').format(selectedDate)).map((booking) {
                      final start = booking['start'] as TimeOfDay;
                      final end = booking['end'] as TimeOfDay;

                      final startHourFraction = start.hour + start.minute / 60.0;
                      final endHourFraction = end.hour + end.minute / 60.0;

                      final top = (startHourFraction - 8) * 100.0;
                      final height = (endHourFraction - startHourFraction) * 100.0;

                      return Positioned(
                        top: top + 25,
                        left: 60,
                        right: 16,
                        child: GestureDetector(
                          onTap: () {
                            showModalBottomSheet(
                              context: context,
                              builder: (_) => BookingDetailsSheet(booking: booking),
                            );
                          },
                          child: Container(
                            height: height,
                            margin: EdgeInsets.only(bottom: 8),
                            padding: EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: booking['type'] == 'Student'
                                  ? Colors.blue.shade100
                                  : Colors.purple.shade100,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(booking['name'], style: TextStyle(fontWeight: FontWeight.bold)),
                                Text(booking['subject']),
                                Text("${start.format(context)} - ${end.format(context)}"),
                              ],
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                ),
              ),
            ),
          )

        ],
      ),
    );
  }
}

class BookingDetailsSheet extends StatelessWidget {
  final Map<String, dynamic> booking;

  const BookingDetailsSheet({required this.booking});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(booking['name'], style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Text("Subject: ${booking['subject']}"),
          Text("Type: ${booking['type']}"),
          Text("Time: ${booking['start'].format(context)} - ${booking['end'].format(context)}"),
          Text("Location: ${booking['location']}"),
          Text("Notes: ${booking['notes']}"),
        ],
      ),
    );
  }
}