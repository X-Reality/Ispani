import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:intl/intl.dart';
import 'package:ispani/BookingData.dart';
import 'package:ispani/BookingCalendarScreen.dart';
import 'package:ispani/Services/paystack_service.dart';
import 'package:ispani/api_key.dart';

class TutorBookingForm extends StatefulWidget {
  final String tutorName;

  TutorBookingForm({required this.tutorName});

  @override
  _TutorBookingFormState createState() => _TutorBookingFormState();
}

class _TutorBookingFormState extends State<TutorBookingForm> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _notesController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();

  String? _selectedSubject;
  String? _selectedPlatform;
  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;
  bool _isPaymentProcessing = false;

  final List<String> _subjects = ['Math', 'Science', 'English', 'History', 'Coding'];
  final List<String> _platforms = ['Zoom', 'Microsoft Teams'];

  final PaystackService _paystackService = PaystackService(ApiKey.secretKey);

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

  Future<bool> _processPayment() async {
    setState(() => _isPaymentProcessing = true);

    try {
      final reference = _generateReference();
      final metadata = {
        'tutor_name': widget.tutorName,
        'subject': _selectedSubject ?? '',
        'date': _selectedDate?.toString() ?? '',
      };

      final authorizationUrl = await _paystackService.initializeTransaction(
        email: _emailController.text.trim(),
        amount: 10000, // ₦100 in kobo
        reference: reference,
        metadata: metadata,
      );

      final paymentSuccess = await _showPaystackWebView(authorizationUrl, reference);

      return paymentSuccess;
    } catch (e) {
      print('Payment error: $e');
      return false;
    } finally {
      setState(() => _isPaymentProcessing = false);
    }
  }

  Future<bool> _showPaystackWebView(String url, String reference) async {
    return await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (context) => SizedBox(
        height: MediaQuery.of(context).size.height * 0.9,
        child: InAppWebView(
          initialUrlRequest: URLRequest(url: WebUri(url)), // Use WebUri here
          onLoadStop: (controller, url) async {
            if (url?.toString().contains('callback') ?? false) {
              Navigator.pop(context, true);
            }
          },
          onLoadError: (controller, url, code, message) {
            Navigator.pop(context, false);
          },
        ),
      ),
    ) ?? false;
  }

  String _generateReference() {
    return 'TUTOR_${DateTime.now().millisecondsSinceEpoch}';
  }

  void _submitForm() async {
    if (_formKey.currentState!.validate()) {
      if (_selectedDate == null || _selectedTime == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please select both date and time.')),
        );
        return;
      }

      if (_emailController.text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please enter your email address.')),
        );
        return;
      }

      final paymentSuccess = await _processPayment();

      if (paymentSuccess) {
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

        BookingData.bookings.add(newBooking);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Payment successful! Booking confirmed.')),
        );

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => BookingCalendarScreen()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Payment cancelled or failed.')),
        );
      }
    }
  }

  @override
  void dispose() {
    _notesController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Book a Tutor")),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _emailController,
                    decoration: InputDecoration(
                      labelText: 'Email Address',
                      border: OutlineInputBorder(),
                      hintText: 'Enter your email for payment receipt',
                    ),
                    keyboardType: TextInputType.emailAddress,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your email';
                      }
                      if (!value.contains('@')) {
                        return 'Please enter a valid email';
                      }
                      return null;
                    },
                  ),
                  SizedBox(height: 16),

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
                      onPressed: _isPaymentProcessing ? null : _submitForm,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: _isPaymentProcessing ? Colors.grey : Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_isPaymentProcessing)
            Container(
              color: Colors.black.withOpacity(0.5),
              child: Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }
}