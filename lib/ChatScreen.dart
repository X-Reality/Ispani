// chat_screen.dart
import 'package:flutter/material.dart';
import 'package:ispani/message_models.dart';
import 'package:ispani/services/message_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ChatScreen extends StatefulWidget {
  final String senderName;
  final String recipientId; // Add recipientId as a parameter

  ChatScreen(
      {required this.senderName,
      required this.recipientId}); // Update constructor

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final MessageService messageService =
      MessageService('http://127.0.0.1:8000/'); // Base URL
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false; // To manage loading state
  List<Message> messages = []; // List to hold messages

  @override
  void initState() {
    super.initState();
    _fetchMessages(); // Fetch messages when the screen initializes
  }

  Future<String?> _getToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  void _sendMessage() async {
    String? token = await _getToken();

    if (token == null) {
      print("No authentication token found.");
      return;
    }

    if (_controller.text.isNotEmpty) {
      setState(() {
        _isLoading = true; // Set loading state
      });

      try {
        // Send the message using the recipientId from the widget and the token
        await messageService.sendMessage(
            _controller.text, widget.recipientId, token);
        _controller.clear();
        // Optionally, show a success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Message sent!")),
        );
        // Fetch messages again to update the UI
        _fetchMessages();
      } catch (e) {
        // Handle error
        print("Error sending message: $e");
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Failed to send message.")),
        );
      } finally {
        setState(() {
          _isLoading = false; // Reset loading state
        });
      }
    }
  }

  void _fetchMessages() async {
    String? token = await _getToken();

    if (token != null) {
      try {
        // Use fetchConversation instead of fetchMessages
        List<Message> fetchedMessages =
            await messageService.fetchConversation(widget.recipientId, token);
        setState(() {
          messages = fetchedMessages; // Update the messages list
        });
      } catch (e) {
        // Handle error
        print("Error fetching messages: $e");
      }
    } else {
      print("No authentication token found.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.senderName),
        backgroundColor: Colors.blue,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                return ListTile(
                  title: Text(
                      message.senderName), // Adjust based on your Message model
                  subtitle: Text(
                      message.content), // Adjust based on your Message model
                  trailing: Text(
                      message.timestamp), // Adjust based on your Message model
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: "Type a message",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _isLoading
                      ? null
                      : _sendMessage, // Disable button while loading
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
