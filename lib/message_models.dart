// message_models.dart
class Message {
  final String id;
  final String senderId;
  final String senderName;
  final String content;
  final String timestamp;
  final String profileImage;

  Message({
    required this.id,
    required this.senderId,
    required this.senderName, 
    required this.content, 
    required this.timestamp,
    required this.profileImage,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? '',
      senderId: json['sender_id'] ?? '',
      senderName: json['sender_name'] ?? 'Unknown',
      content: json['content'] ?? '',
      timestamp: json['timestamp'] ?? '',
      profileImage: json['profile_image'] ?? 'assets/default_avatar.png',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'sender_name': senderName,
      'content': content,
      'timestamp': timestamp,
      'profile_image': profileImage,
    };
  }
}