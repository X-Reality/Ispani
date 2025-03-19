class User {
  final int id;
  final String username;
  final String email;
  final String? photoUrl;

  User({
    required this.id,
    required this.username,
    required this.email,
    this.photoUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      photoUrl: json['photo_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'photo_url': photoUrl,
    };
  }
}

class Message {
  final int id;
  final String content;
  final DateTime timestamp;
  final User sender;
  final String? attachmentUrl;

  Message({
    required this.id,
    required this.content,
    required this.timestamp,
    required this.sender,
    this.attachmentUrl,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
      sender: User.fromJson(json['sender']),
      attachmentUrl: json['attachment_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'sender': sender.toJson(),
      'attachment_url': attachmentUrl,
    };
  }
}

class Group {
  final int id;
  final String name;
  final String? description;
  final String? course;
  final int? yearOfStudy;
  final List<User>? members;
  final List<Message>? messages;
  final DateTime createdAt;
  final User? createdBy;

  Group({
    required this.id,
    required this.name,
    this.description,
    this.course,
    this.yearOfStudy,
    this.members,
    this.messages,
    required this.createdAt,
    this.createdBy,
  });

  factory Group.fromJson(Map<String, dynamic> json) {
    List<User>? membersList;
    if (json['members'] != null) {
      membersList = (json['members'] as List)
          .map((memberJson) => User.fromJson(memberJson))
          .toList();
    }

    List<Message>? messagesList;
    if (json['messages'] != null) {
      messagesList = (json['messages'] as List)
          .map((messageJson) => Message.fromJson(messageJson))
          .toList();
    }

    return Group(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      course: json['course'],
      yearOfStudy: json['year_of_study'],
      members: membersList,
      messages: messagesList,
      createdAt: DateTime.parse(json['created_at']),
      createdBy: json['created_by'] != null ? User.fromJson(json['created_by']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'course': course,
      'year_of_study': yearOfStudy,
      'created_at': createdAt.toIso8601String(),
      'created_by': createdBy?.toJson(),
    };
  }
}