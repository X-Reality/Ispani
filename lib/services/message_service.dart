// message_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:ispani/message_models.dart';

class MessageService {
  final String baseUrl;

  MessageService(this.baseUrl);

  // Fetch all messages for inbox - with token parameter
  Future<List<Message>> fetchMessages(String token) async {
    final response = await http.get(
      Uri.parse('${baseUrl}messages/private/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Message.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load messages: ${response.statusCode}');
    }
  }

  // Fetch conversation with specific recipient
  Future<List<Message>> fetchConversation(
      String recipientId, String token) async {
    final response = await http.get(
      Uri.parse('${baseUrl}messages/private/inbox/$recipientId/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Message.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load conversation: ${response.statusCode}');
    }
  }

  // Send a message
  Future<void> sendMessage(
      String content, String recipientId, String token) async {
    final response = await http.post(
      Uri.parse('${baseUrl}messages/private/send/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'recipient': recipientId,
        'content': content,
      }),
    );

    if (response.statusCode != 201) {
      throw Exception('Failed to send message: ${response.statusCode}');
    }
  }
}
