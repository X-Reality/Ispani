import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:ispani/BookingData.dart';

class BookingCalendarScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final bookings = BookingData.bookings;

    return Scaffold(
      appBar: AppBar(
        title: Text("Your Calendar"),
      ),
      body: bookings.isEmpty
          ? Center(child: Text("No bookings yet."))
          : ListView.builder(
        itemCount: bookings.length,
        itemBuilder: (context, index) {
          final booking = bookings[index];
          final dateStr = DateFormat('EEEE, MMM d, y').format(booking.dateTime);
          final timeStr = DateFormat.jm().format(booking.dateTime);

          return Card(
            margin: EdgeInsets.all(8),
            child: ListTile(
              leading: Icon(Icons.event_note),
              title: Text("${booking.subject} with ${booking.tutorName}"),
              subtitle: Text("$dateStr at $timeStr\nVia ${booking.platform}"
                  "${booking.notes.isNotEmpty ? "\nNotes: ${booking.notes}" : ""}"),
            ),
          );
        },
      ),
    );
  }
}
