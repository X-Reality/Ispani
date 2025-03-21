// messages_screen.dart
import 'package:flutter/material.dart';
import 'package:ispani/ChatScreen.dart';
import 'package:ispani/message_models.dart';
import 'package:ispani/services/message_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MessagesScreen extends StatefulWidget {
  @override
  _MessagesScreenState createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  // Change this to use the base URL, not the full endpoint
  final MessageService messageService =
      MessageService('http://127.0.0.1:8000/');
  List<Message> messages = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchMessages();
  }

  Future<void> _fetchMessages() async {
    try {
      final token = await _getToken(); // Get the token from Shared Preferences
      if (token != null) {
        final fetchedMessages = await messageService.fetchMessages(token);
        setState(() {
          messages = fetchedMessages;
          isLoading = false;
        });
      } else {
        // Handle the case where the token is null (e.g., show an error message)
        setState(() {
          isLoading = false;
        });
      }
    } catch (e) {
      // Handle error
      print("Error fetching messages: $e");
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<String?> _getToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

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
            builder: (context) => ChatScreen(
              senderName: message.senderName,
              recipientId:
                  message.senderId, // Make sure to pass the senderId here
            ),
          ),
        );
      },
    );
  }
}
