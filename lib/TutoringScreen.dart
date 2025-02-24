import 'package:flutter/material.dart';

class BookTutorScreen extends StatefulWidget {
  @override
  _BookTutorScreenState createState() => _BookTutorScreenState();
}

class _BookTutorScreenState extends State<BookTutorScreen> {
  String selectedDay = '';
  String selectedTime = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Book a Tutor'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTutorList(),
            SizedBox(height: 20),
            _buildTutorProfile(),
            SizedBox(height: 20),
            _buildCalendarSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildTutorList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Industrial Engineering Tutors', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        SizedBox(height: 10),
        _buildModuleItem('Maths III', true),
        _buildModuleItem('Mechanics II', true),
        _buildModuleItem('Stats IV', false),
        Divider(),
        _buildTutorRating('Mr Kitso', 2),
        _buildTutorRating('Ms Karabo', 1),
        _buildTutorRating('Ms Dineo', 4),
      ],
    );
  }

  Widget _buildModuleItem(String module, bool isVisible) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(module),
        TextButton(
          onPressed: () {},
          child: Text(isVisible ? 'View' : 'Hide'),
        )
      ],
    );
  }

  Widget _buildTutorRating(String name, int stars) {
    return ListTile(
      leading: Icon(Icons.person),
      title: Text(name),
      subtitle: Row(
        children: List.generate(5, (index) => Icon(
          index < stars ? Icons.star : Icons.star_border,
        )),
      ),
    );
  }

  Widget _buildTutorProfile() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(radius: 30),
                SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Ms Dineo Mbedi', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      Text('3-star rating'),
                      Text('3rd year student with 5+ distinctions')
                    ],
                  ),
                )
              ],
            ),
            SizedBox(height: 10),
            Text('Modules Tutored: Maths, Stats IV'),
            SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildProfileStat('Distinctions', '5+'),
                _buildProfileStat('Students Tutored', '13+'),
                _buildProfileStat('Sessions', '5+'),
              ],
            ),
            SizedBox(height: 10),
            ElevatedButton(
              onPressed: () {},
              child: Text('Book Tutor'),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildProfileStat(String title, String value) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        Text(title)
      ],
    );
  }

  Widget _buildCalendarSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Ms Dineo's Calendar", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        SizedBox(height: 10),
        Wrap(
          spacing: 8,
          children: List.generate(14, (index) {
            String day = (index + 1).toString();
            return ChoiceChip(
              label: Text(day),
              selected: selectedDay == day,
              onSelected: (selected) {
                setState(() {
                  selectedDay = selected ? day : '';
                });
              },
            );
          }),
        ),
        SizedBox(height: 20),
        if (selectedDay.isNotEmpty) _buildTimeSlots()
      ],
    );
  }

  Widget _buildTimeSlots() {
    final slots = [
      {'time': '9:00 - 10:00', 'status': 'Available'},
      {'time': '12:00 - 13:00', 'status': 'Available'},
      {'time': '16:00 - 17:00', 'status': 'Public session booked'},
    ];

    return Column(
      children: slots.map((slot) {
        return ListTile(
          title: Text(slot['time']!),
          subtitle: Text(slot['status']!),
          trailing: ElevatedButton(
            onPressed: slot['status'] == 'Available'
                ? () {
              setState(() {
                selectedTime = slot['time']!;
              });
            }
                : null,
            child: Text(slot['status'] == 'Available' ? 'Book Slot' : 'Request to Join'),
          ),
        );
      }).toList(),
    );
  }
}
