// messages_screen.dart
import 'package:flutter/material.dart';
import 'package:ispani/ChatScreen.dart';
import 'package:ispani/message_models.dart';
import 'package:ispani/services/message_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MessagesScreen extends StatelessWidget {
  final List<Message> messages = [
    Message(
      senderName: "Alice",
      message: "Hey! How's it going?",
      time: "10:30 AM",
      profileImage: "assets/profile1.jpg",
    ),
    Message(
      senderName: "Bob",
      message: "Let's catch up tomorrow.",
      time: "9:15 AM",
      profileImage: "assets/profile2.jpg",
    ),
    Message(
      senderName: "Charlie",
      message: "I sent you the files.",
      time: "Yesterday",
      profileImage: "assets/profile3.jpg",
    ),
    Message(
      senderName: "Daisy",
      message: "Can you call me back?",
      time: "Monday",
      profileImage: "assets/profile4.jpg",
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text("Messages"),
        backgroundColor: Colors.white,
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return _buildMessageItem(context, messages[index]);
              },
            ),
    );
  }

  Widget _buildMessageItem(BuildContext context, Message message) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: AssetImage(message.profileImage),
      ),
      title: Text(
        message.senderName,
        style: TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Text(
        message.content,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Text(
        message.timestamp,
        style: TextStyle(color: Colors.grey),
      ),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ChatScreen(senderName: message.senderName),
          ),
        );
      },
    );
  }
}

class Message {
  final String senderName;
  final String message;
  final String time;
  final String profileImage;

  Message({
    required this.senderName,
    required this.message,
    required this.time,
    required this.profileImage,
  });
}

class ChatScreen extends StatelessWidget {
  final String senderName;

  ChatScreen({required this.senderName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(senderName),
        backgroundColor: Colors.blue,
      ),
      body: Center(
        child: Text("Chat with $senderName"),
      ),
    );
  }
}
