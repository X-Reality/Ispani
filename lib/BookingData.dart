class Booking {
  final String tutorName;
  final DateTime dateTime;
  final String subject;
  final String platform;
  final String notes;

  Booking({
    required this.tutorName,
    required this.dateTime,
    required this.subject,
    required this.platform,
    required this.notes,
  });
}

class BookingData {
  static List<Booking> bookings = [];
}
