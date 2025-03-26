class Group {
  final int id;
  final String name;
  final String description;

  Group({required this.id, required this.name, required this.description});

  factory Group.fromJson(Map<String, dynamic> json) {
    return Group(
      id: json['id'],
      name: json['name'],
      description: json['description'],
    );
  }
}
