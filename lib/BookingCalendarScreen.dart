import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:ispani/BookingData.dart';
import 'package:table_calendar/table_calendar.dart';

class BookingCalendarScreen extends StatefulWidget {
  @override
  _BookingCalendarScreenState createState() => _BookingCalendarScreenState();
}

class _BookingCalendarScreenState extends State<BookingCalendarScreen> {
  late Map<DateTime, List<Booking>> _events;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;

  @override
  void initState() {
    super.initState();
    _selectedDay = _focusedDay;
    _generateEventsMap();
  }

  void _generateEventsMap() {
    _events = {};

    for (var booking in BookingData.bookings) {
      final date = DateTime(booking.dateTime.year, booking.dateTime.month, booking.dateTime.day);
      if (_events[date] == null) {
        _events[date] = [booking];
      } else {
        _events[date]!.add(booking);
      }
    }
  }

  List<Booking> _getEventsForDay(DateTime day) {
    final date = DateTime(day.year, day.month, day.day);
    return _events[date] ?? [];
  }

  @override
  Widget build(BuildContext context) {
    final eventsForSelectedDay = _getEventsForDay(_selectedDay!);

    return Scaffold(
      appBar: AppBar(
        title: Text("Your Calendar"),
      ),
      body: Column(
        children: [
          TableCalendar<Booking>(
            firstDay: DateTime.utc(2020, 1, 1),
            lastDay: DateTime.utc(2100, 12, 31),
            focusedDay: _focusedDay,
            selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
            onDaySelected: (selected, focused) {
              setState(() {
                _selectedDay = selected;
                _focusedDay = focused;
              });
            },
            calendarFormat: CalendarFormat.month,
            eventLoader: _getEventsForDay,
            calendarStyle: CalendarStyle(
              todayDecoration: BoxDecoration(
                color: Colors.green.shade200,
                shape: BoxShape.circle,
              ),
              selectedDecoration: BoxDecoration(
                color: Colors.green,
                shape: BoxShape.circle,
              ),
              markerDecoration: BoxDecoration(
                color: Colors.green.shade700,
                shape: BoxShape.circle,
              ),
            ),
          ),
          Divider(),
          Expanded(
            child: eventsForSelectedDay.isEmpty
                ? Center(child: Text("No bookings for selected date."))
                : ListView.builder(
              itemCount: eventsForSelectedDay.length,
              itemBuilder: (context, index) {
                final booking = eventsForSelectedDay[index];
                final timeStr = DateFormat.jm().format(booking.dateTime);
                return Card(
                  margin: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  child: ListTile(
                    leading: Icon(Icons.book_online),
                    title: Text("${booking.subject} with ${booking.tutorName}"),
                    subtitle: Text("Time: $timeStr\nVia ${booking.platform}"
                        "${booking.notes.isNotEmpty ? "\nNotes: ${booking.notes}" : ""}"),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
