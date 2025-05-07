import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'RescheduleScreen.dart';

// Custom Bottom Navigation Bar
class CustomBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  CustomBottomNavigationBar({required this.currentIndex, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      type: BottomNavigationBarType.fixed,
      currentIndex: currentIndex,
      onTap: onTap,
      selectedItemColor: Color.fromARGB(255, 147, 182, 138),
      unselectedItemColor: Colors.grey,
      backgroundColor: Colors.white,
      items: [
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: "Home",
        ),
        BottomNavigationBarItem(icon: Icon(Icons.message), label: "Messages"),
        BottomNavigationBarItem(
          icon: Container(
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Color.fromARGB(255, 147, 182, 138),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.explore, color: Colors.white),
          ),
          label: "",
        ),
        BottomNavigationBarItem(
            icon: Icon(Icons.supervised_user_circle), label: "Groups"),
        BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
      ],
    );
  }
}

class TutorHomeScreen extends StatefulWidget {
  const TutorHomeScreen({super.key});

  @override
  State<TutorHomeScreen> createState() => _TutorHomeScreenState();
}

class _TutorHomeScreenState extends State<TutorHomeScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  final Color green = const Color(0xFF2E8B57);
  final Color lightGreen = const Color(0xFFA8D5BA);
  String dropdownValue = "Sort";
  int _currentIndex = 0;

  final List<Map<String, String>> todaysBookings = [
    {
      'student': 'John Doe',
      'subject': 'Mathematics',
      'time': '10:00 AM',
      'date': '2025-05-01',
      'type': 'Student',
    },
    {
      'student': 'Jane Smith',
      'subject': 'Science',
      'time': '1:00 PM',
      'date': '2025-05-01',
      'type': 'High School Learner',
    },
  ];

  final List<Map<String, String>> upcomingClasses = [
    {
      'student': 'Leo Thomas',
      'subject': 'English',
      'time': '2:00 PM',
      'date': '2025-05-03',
      'type': 'Student',
    },
    {
      'student': 'Emily White',
      'subject': 'Biology',
      'time': '3:30 PM',
      'date': '2025-05-04',
      'type': 'High School Learner',
    },
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _onRefresh() async {
    await Future.delayed(Duration(seconds: 1));
    setState(() {});
  }

  void _showBookingDrawer(Map<String, String> booking) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text("Booking Details",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            ListTile(
                leading: Icon(Icons.person, color: green),
                title: Text(booking['student'] ?? ''),
                subtitle: Text(booking['type'] ?? '')),
            ListTile(
                leading: Icon(Icons.book, color: green),
                title: Text("Subject: ${booking['subject']}")),
            ListTile(
                leading: Icon(Icons.calendar_today, color: green),
                title: Text("Date: ${booking['date']}")),
            ListTile(
                leading: Icon(Icons.access_time, color: green),
                title: Text("Time: ${booking['time']}")),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  builder: (context) => Wrap(
                    children: [
                      ListTile(
                        leading: Icon(Icons.check, color: green),
                        title: Text("Approve"),
                        onTap: () {
                          Navigator.pop(context);
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                              content: Text(
                                  "Booking approved for ${booking['student']}")));
                        },
                      ),
                      ListTile(
                        leading: Icon(Icons.close, color: Colors.red),
                        title: Text("Decline"),
                        onTap: () {
                          Navigator.pop(context);
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                              content: Text(
                                  "Booking declined for ${booking['student']}")));
                        },
                      ),
                      ListTile(
                        leading: Icon(Icons.schedule, color: Colors.orange),
                        title: Text("Reschedule"),
                        onTap: () {
                          Navigator.pop(context);
                          Navigator.pop(context);
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => RescheduleScreen(
                                studentName: booking['student'] ?? '',
                                subject: booking['subject'] ?? '',
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: green,
                minimumSize: Size(double.infinity, 48),
              ),
              child: Text("Take Action", style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textColor = Colors.black;
    final actionColor = Color.fromARGB(255, 147, 182, 138);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "Search",
                  filled: true,
                  fillColor: Colors.grey[200],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: Icon(Icons.search, color: Colors.grey),
                ),
              ),
            ),
            SizedBox(width: 10),
            CircleAvatar(backgroundImage: AssetImage("assets/images (1).jpeg")),
          ],
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _onRefresh,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            // Earnings Circle
            GestureDetector(
              onTap: () => _animationController
                  .forward()
                  .then((_) => _animationController.reverse()),
              child: Center(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    for (double radius in [270, 330, 400])
                      Container(
                        width: radius,
                        height: radius,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                              color: green.withOpacity(0.2), width: 2),
                        ),
                      ),
                    ScaleTransition(
                      scale: _scaleAnimation,
                      child: Container(
                        width: 220,
                        height: 220,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: green,
                          boxShadow: [
                            BoxShadow(
                                color: green.withOpacity(0.4),
                                blurRadius: 16,
                                offset: Offset(0, 8))
                          ],
                        ),
                        child: Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text("Earnings",
                                  style: TextStyle(
                                      fontSize: 16, color: Colors.white)),
                              SizedBox(height: 4),
                              Text("R1200",
                                  style: TextStyle(
                                      fontSize: 26,
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Today's Bookings",
                    style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: textColor)),
                Text("View all",
                    style: TextStyle(fontSize: 17, color: actionColor)),
              ],
            ),
            SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: todaysBookings.map((booking) {
                  return GestureDetector(
                    onTap: () => _showBookingDrawer(booking),
                    child: Container(
                      width: 280,
                      margin: EdgeInsets.only(right: 16),
                      padding: EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.green[300],
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                              color: Colors.grey.shade300,
                              blurRadius: 10,
                              offset: Offset(0, 4))
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.school, color: green, size: 20),
                              SizedBox(width: 8),
                              Expanded(
                                  child: Text(booking['student']!,
                                      style: TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                          color: Colors
                                              .white))), // Bold and white text color
                            ],
                          ),
                          SizedBox(height: 10),
                          Text("Subject: ${booking['subject']}",
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight
                                      .bold)), // Bold and white text color
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(Icons.calendar_today,
                                  size: 16,
                                  color: Colors.white), // White icon color
                              SizedBox(width: 6),
                              Text(booking['date']!,
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight
                                          .bold)), // Bold and white text color
                              SizedBox(width: 12),
                              Icon(Icons.access_time,
                                  size: 16,
                                  color: Colors.white), // White icon color
                              SizedBox(width: 6),
                              Text(booking['time']!,
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight
                                          .bold)), // Bold and white text color
                            ],
                          ),
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(Icons.person_pin,
                                  size: 16,
                                  color: Colors.white), // White icon color
                              SizedBox(width: 6),
                              Text(booking['type'] ?? 'Student',
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight
                                          .bold)), // Bold and white text color
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Upcoming classes",
                    style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: textColor)),
                Text("View all",
                    style: TextStyle(fontSize: 17, color: actionColor)),
              ],
            ),
            SizedBox(height: 12),
            ...upcomingClasses.map((cls) {
              return GestureDetector(
                onTap: () => _showBookingDrawer(cls),
                child: Container(
                  margin: EdgeInsets.only(bottom: 16),
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(cls['student']!,
                                  style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: green)),
                              SizedBox(height: 6),
                              Text("Subject: ${cls['subject']}",
                                  style: TextStyle(color: textColor)),
                              SizedBox(height: 6),
                              Row(children: [
                                Icon(Icons.calendar_today,
                                    size: 16, color: textColor),
                                SizedBox(width: 4),
                                Text(cls['date']!),
                                SizedBox(width: 12),
                                Icon(Icons.access_time,
                                    size: 16, color: textColor),
                                SizedBox(width: 4),
                                Text(cls['time']!),
                              ]),
                            ]),
                      ),
                      Icon(Icons.chevron_right, size: 30, color: green),
                    ],
                  ),
                ),
              );
            }).toList(),
            SizedBox(height: 30),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2.0),
              child: Material(
                elevation: 4,
                shadowColor: Colors.grey.withOpacity(
                    0.3), // Set shadow color to gray with 0.3 opacity
                borderRadius: BorderRadius.circular(16),
                child: Container(
                  decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16)),
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text("Today's Bookings",
                              style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: textColor)),
                          // Define the state for the dropdown value

                          Container(
                            decoration: BoxDecoration(
                              color: Colors.white, // White background
                              borderRadius: BorderRadius.circular(
                                  30.0), // Rounded corners
                              border: Border.all(
                                color: Colors.green, // Green border
                                width: 1.0, // Border width
                              ),
                            ),
                            padding: EdgeInsets.symmetric(
                                horizontal: 16.0,
                                vertical:
                                    0.01), // Reduced top and bottom padding
                            child: DropdownButton<String>(
                              value: dropdownValue,
                              onChanged: (String? value) {
                                setState(() {
                                  dropdownValue = value ??
                                      "Sort"; // Update the dropdown value on selection change
                                });
                              },
                              underline:
                                  SizedBox(), // Remove the default underline
                              icon: Icon(
                                Icons.chevron_right, // Chevron right icon
                                color: Colors.green, // Icon color
                              ),
                              items: <String>[
                                'Sort',
                                'Option 1',
                                'Option 2'
                              ].map<DropdownMenuItem<String>>((String value) {
                                return DropdownMenuItem<String>(
                                  value: value,
                                  child: Text(
                                    value,
                                    style: TextStyle(
                                        color: Colors.black,
                                        fontSize: 12.0), // Text color (black)
                                  ),
                                );
                              }).toList(),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 16),
                      AspectRatio(
                        aspectRatio: 1.6,
                        child: BarChart(
                          BarChartData(
                            alignment: BarChartAlignment.spaceAround,
                            maxY: 10,
                            barTouchData: BarTouchData(enabled: false),
                            gridData: FlGridData(show: false),
                            titlesData: FlTitlesData(
                              leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                      showTitles: true, reservedSize: 28)),
                              rightTitles: AxisTitles(
                                  sideTitles: SideTitles(showTitles: false)),
                              topTitles: AxisTitles(
                                  sideTitles: SideTitles(showTitles: false)),
                              bottomTitles: AxisTitles(
                                sideTitles: SideTitles(
                                  showTitles: true,
                                  getTitlesWidget: (value, meta) {
                                    const days = [
                                      'Mon',
                                      'Tue',
                                      'Wed',
                                      'Thu',
                                      'Fri',
                                      'Sat',
                                      'Sun'
                                    ];
                                    return Text(days[value.toInt()],
                                        style: TextStyle(
                                            color: Colors.grey[600],
                                            fontSize: 12));
                                  },
                                  reservedSize: 32,
                                ),
                              ),
                            ),
                            borderData: FlBorderData(show: false),
                            barGroups: List.generate(7, (i) {
                              final heights = [6, 4, 7, 8, 5, 6, 4];
                              return BarChartGroupData(x: i, barRods: [
                                BarChartRodData(
                                    toY: heights[i].toDouble(),
                                    color: green,
                                    width: 16)
                              ]);
                            }),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: CustomBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
      ),
    );
  }
}
