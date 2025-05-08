class Group {
  final int id;
  final String name;
  final String city;
  final String institution;
  final List<String> hobbies;

  Group({
    required this.id,
    required this.name,
    required this.city,
    required this.institution,
    required this.hobbies,
  });

  factory Group.fromJson(Map<String, dynamic> json) {
    return Group(
      id: json['id'],
      name: json['name'],
      city: json['city'],
      institution: json['institution'] ?? '',
      hobbies: List<String>.from(json['hobbies'] ?? []),
    );
  }
}
