import 'package:flutter/material.dart';

class RescheduleScreen extends StatefulWidget {
  final String studentName;
  final String subject;

  const RescheduleScreen({super.key, required this.studentName, required this.subject});

  @override
  State<RescheduleScreen> createState() => _RescheduleScreenState();
}

class _RescheduleScreenState extends State<RescheduleScreen> {
  DateTime? selectedDate;
  TimeOfDay? selectedTime;

  final Color green = Color(0xFF1B5E20); // Norwegian green

  void _pickDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: selectedDate ?? DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(Duration(days: 365)),
    );
    if (date != null) setState(() => selectedDate = date);
  }

  void _pickTime() async {
    final time = await showTimePicker(
      context: context,
      initialTime: selectedTime ?? TimeOfDay.now(),
    );
    if (time != null) setState(() => selectedTime = time);
  }

  void _confirmReschedule() {
    if (selectedDate == null || selectedTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select both date and time.')),
      );
      return;
    }

    // You can pass back the new date/time or handle logic here
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text('Class rescheduled to ${selectedDate!.toLocal().toString().split(" ")[0]} at ${selectedTime!.format(context)}'),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text("Reschedule Class"),
        backgroundColor: green,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Student: ${widget.studentName}",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
            ),
            Text(
              "Subject: ${widget.subject}",
              style: TextStyle(fontSize: 16, color: Colors.grey[700]),
            ),
            SizedBox(height: 32),
            Text("New Date", style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            InkWell(
              onTap: _pickDate,
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      selectedDate != null
                          ? "${selectedDate!.toLocal().toString().split(' ')[0]}"
                          : "Select a date",
                      style: TextStyle(fontSize: 16),
                    ),
                    Icon(Icons.calendar_today_outlined, color: green),
                  ],
                ),
              ),
            ),
            SizedBox(height: 24),
            Text("New Time", style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            InkWell(
              onTap: _pickTime,
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      selectedTime != null
                          ? selectedTime!.format(context)
                          : "Select a time",
                      style: TextStyle(fontSize: 16),
                    ),
                    Icon(Icons.access_time_outlined, color: green),
                  ],
                ),
              ),
            ),
            Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _confirmReschedule,
                style: ElevatedButton.styleFrom(
                  backgroundColor: green,
                  padding: EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  "Confirm Reschedule",
                  style: TextStyle(fontSize: 16, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
