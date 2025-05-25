import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

class TutorBookingForm extends StatefulWidget {
  final String tutorName;

  const TutorBookingForm({Key? key, required this.tutorName}) : super(key: key);

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
  bool _isOnline = true;

  final List<String> _subjects = ['Math', 'Science', 'English', 'History', 'Coding'];
  final List<String> _platforms = ['Zoom', 'Microsoft Teams'];

  final String tutorAddress = "123 Tutor Street, Cape Town, South Africa";

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

  Future<void> _openMap(String address) async {
    final Uri mapUri = Uri.parse("https://www.google.com/maps/search/?api=1&query=${Uri.encodeComponent(address)}");

    try {
      if (!await launchUrl(mapUri, mode: LaunchMode.externalApplication)) {
        throw Exception('Could not launch map');
      }
    } catch (e) {
      print("Map error: $e");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Could not open map. Please check your connection.")),
      );
    }
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      if (_selectedDate == null || _selectedTime == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please select both date and time.')),
        );
        return;
      }

      final formattedDate = _formatDate(_selectedDate);
      final formattedTime = _formatTime(_selectedTime);
      final meetingLink = "https://example.com/fake-meeting-link";

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
              if (_isOnline) Text("Platform: $_selectedPlatform") else Text("Address: $tutorAddress"),
              Text("Date: $formattedDate"),
              Text("Time: $formattedTime"),
              if (_notesController.text.isNotEmpty)
                Text("Notes: ${_notesController.text}"),
              if (_isOnline)
                ...[
                  SizedBox(height: 10),
                  Text("Meeting Link:"),
                  Text(meetingLink, style: TextStyle(color: Colors.blue)),
                ]
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
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
    final green = Color(0xFF2E8B57); // Norwegian green

    return Scaffold(
      appBar: AppBar(
        title: Text("Book a Tutor"),
        backgroundColor: green,
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ElevatedButton.icon(
          icon: Icon(Icons.check),
          label: Text('Submit Booking'),
          onPressed: _submitForm,
          style: ElevatedButton.styleFrom(
            backgroundColor: green,
            foregroundColor: Colors.white,
            padding: EdgeInsets.symmetric(vertical: 16),
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              // Tutor Detail Card
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.grey[300],
                    child: Icon(Icons.person, color: Colors.white),
                  ),
                  title: Text(widget.tutorName, style: TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Subject: Math"),
                      Text("Email: tutor@example.com"),
                      Text("Phone: +27 123 456 7890"),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 16),

              // Subject Dropdown
              DropdownButtonFormField<String>(
                decoration: InputDecoration(
                  labelText: 'Select Subject',
                  border: OutlineInputBorder(),
                ),
                value: _selectedSubject,
                items: _subjects.map((subject) => DropdownMenuItem(
                  value: subject,
                  child: Text(subject),
                )).toList(),
                onChanged: (value) => setState(() => _selectedSubject = value),
                validator: (value) => value == null ? 'Please select a subject' : null,
              ),
              SizedBox(height: 16),

              // Online / Physical Toggle
              Text("Booking Type", style: TextStyle(fontWeight: FontWeight.bold)),
              Row(
                children: [
                  Expanded(
                    child: RadioListTile<bool>(
                      title: Text("Online"),
                      value: true,
                      groupValue: _isOnline,
                      onChanged: (value) => setState(() => _isOnline = value!),
                    ),
                  ),
                  Expanded(
                    child: RadioListTile<bool>(
                      title: Text("Physical"),
                      value: false,
                      groupValue: _isOnline,
                      onChanged: (value) => setState(() => _isOnline = value!),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 16),

              // Platform or Address
              _isOnline
                  ? DropdownButtonFormField<String>(
                decoration: InputDecoration(
                  labelText: 'Select Meeting Platform',
                  border: OutlineInputBorder(),
                ),
                value: _selectedPlatform,
                items: _platforms.map((platform) => DropdownMenuItem(
                  value: platform,
                  child: Text(platform),
                )).toList(),
                onChanged: (value) => setState(() => _selectedPlatform = value),
                validator: (value) =>
                value == null && _isOnline ? 'Please select a platform' : null,
              )
                  : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Address: $tutorAddress"),
                  SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: () => _openMap(tutorAddress),
                    icon: Icon(Icons.directions),
                    label: Text("Get Directions"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),

              SizedBox(height: 16),

              // Date Picker
              ListTile(
                title: Text(_formatDate(_selectedDate)),
                trailing: Icon(Icons.calendar_today),
                onTap: _pickDate,
              ),

              // Time Picker
              ListTile(
                title: Text(_formatTime(_selectedTime)),
                trailing: Icon(Icons.access_time),
                onTap: _pickTime,
              ),

              // Notes
              TextFormField(
                controller: _notesController,
                decoration: InputDecoration(
                  labelText: 'Special Notes',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              SizedBox(height: 80),
            ],
          ),
        ),
      ),
    );
  }
}
