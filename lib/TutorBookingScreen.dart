import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:ispani/BookingData.dart';
import 'package:ispani/BookingCalendarScreen.dart';

class TutorBookingForm extends StatefulWidget {
  final String tutorName;

  TutorBookingForm({required this.tutorName});

  @override
  _TutorBookingFormState createState() => _TutorBookingFormState();
}

class _TutorBookingFormState extends State<TutorBookingForm> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _notesController = TextEditingController();

  String? _selectedSubject;
  String? _selectedPlatform;
  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;

  final List<String> _subjects = ['Math', 'Science', 'English', 'History', 'Coding'];
  final List<String> _platforms = ['Zoom', 'Microsoft Teams'];

  String _formatDate(DateTime? date) {
    if (date == null) return 'Pick a date';
    return DateFormat('EEEE, MMM d, y').format(date);
  }

  String _formatTime(TimeOfDay? time) {
    if (time == null) return 'Pick a time';
    final now = DateTime.now();
    final dt = DateTime(now.year, now.month, now.day, time.hour, time.minute);
    return DateFormat.jm().format(dt);
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime(2100),
    );
    if (picked != null) setState(() => _selectedDate = picked);
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime ?? TimeOfDay.now(),
    );
    if (picked != null) setState(() => _selectedTime = picked);
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      if (_selectedDate == null || _selectedTime == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please select both date and time.')),
        );
        return;
      }

      final bookingDateTime = DateTime(
        _selectedDate!.year,
        _selectedDate!.month,
        _selectedDate!.day,
        _selectedTime!.hour,
        _selectedTime!.minute,
      );

      final newBooking = Booking(
        tutorName: widget.tutorName,
        dateTime: bookingDateTime,
        subject: _selectedSubject!,
        platform: _selectedPlatform!,
        notes: _notesController.text,
      );

      // Show confirmation dialog
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text("Booking Confirmed"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Tutor: ${widget.tutorName}"),
              Text("Subject: $_selectedSubject"),
              Text("Platform: $_selectedPlatform"),
              Text("Date: ${_formatDate(_selectedDate)}"),
              Text("Time: ${_formatTime(_selectedTime)}"),
              if (_notesController.text.isNotEmpty)
                Text("Notes: ${_notesController.text}"),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close dialog

                // Save booking
                BookingData.bookings.add(newBooking);

                // Show success snackbar
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Booking successfully added!')),
                );

                // Navigate to calendar
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) => BookingCalendarScreen(),
                  ),
                );
              },
              child: Text("OK"),
            )
          ],
        ),
      );
    }
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Book a Tutor")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: 'Select Subject', border: OutlineInputBorder()),
                value: _selectedSubject,
                items: _subjects
                    .map((subject) => DropdownMenuItem(value: subject, child: Text(subject)))
                    .toList(),
                onChanged: (value) => setState(() => _selectedSubject = value),
                validator: (value) => value == null ? 'Please select a subject' : null,
              ),
              SizedBox(height: 16),

              DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: 'Select Meeting Platform', border: OutlineInputBorder()),
                value: _selectedPlatform,
                items: _platforms
                    .map((platform) => DropdownMenuItem(value: platform, child: Text(platform)))
                    .toList(),
                onChanged: (value) => setState(() => _selectedPlatform = value),
                validator: (value) => value == null ? 'Please select a platform' : null,
              ),
              SizedBox(height: 16),

              ListTile(
                title: Text(_formatDate(_selectedDate)),
                trailing: Icon(Icons.calendar_today),
                onTap: _pickDate,
              ),

              ListTile(
                title: Text(_formatTime(_selectedTime)),
                trailing: Icon(Icons.access_time),
                onTap: _pickTime,
              ),

              TextFormField(
                controller: _notesController,
                decoration: InputDecoration(labelText: 'Special Notes', border: OutlineInputBorder()),
                maxLines: 3,
              ),

              SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: Icon(Icons.check),
                  label: Text('Submit Booking'),
                  onPressed: _submitForm,
                  style: ElevatedButton.styleFrom(padding: EdgeInsets.symmetric(vertical: 16)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
