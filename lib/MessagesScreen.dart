import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ispani/ChatScreen.dart';

class MessagesScreen extends StatefulWidget {
  @override
  _MessagesScreenState createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  List<dynamic> messages = [];
  final String apiUrl =
      "http://127.0.0.1:8000/rooms/{widget.room.Id}/messages/";
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchMessages();
  }

  Future<void> fetchMessages() async {
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? token = prefs.getString("access_token");

      if (token == null) {
        print("No authentication token found.");
        setState(() {
          isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse(apiUrl),
        headers: {"Authorization": "Bearer $token"},
      );

      if (response.statusCode == 200) {
        setState(() {
          messages = json.decode(response.body);
          isLoading = false;
        });
      } else {
        print("Failed to load messages: ${response.statusCode}");
        setState(() {
          isLoading = false;
        });
      }
    } catch (error) {
      print("Error fetching messages: $error");
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> sendMessage(int recipientId, String content) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? token = prefs.getString("access_token");

    if (token == null) {
      print("No authentication token found.");
      return;
    }

    final response = await http.post(
      Uri.parse("http://127.0.0.1:8000/private-chats/"),
      body: jsonEncode({"recipient_id": recipientId, "content": content}),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $token"
      },
    );

    if (response.statusCode == 201) {
      print("Message sent successfully");
      fetchMessages(); // Refresh list
    } else {
      print("Failed to send message: ${response.statusCode}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: Text(
          "Messages",
          style: TextStyle(
            color: Colors.black,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.search, color: Colors.black),
            onPressed: () {
              // Implement search functionality
            },
          ),
        ],
      ),
      body: isLoading
          ? Center(
              child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(
                  Color.fromARGB(255, 147, 182, 138)),
            ))
          : messages.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.message_outlined,
                          size: 70, color: Colors.grey[400]),
                      SizedBox(height: 16),
                      Text(
                        "No messages yet",
                        style: TextStyle(
                            fontSize: 18,
                            color: Colors.grey[600],
                            fontWeight: FontWeight.w500),
                      ),
                      SizedBox(height: 8),
                      Text(
                        "Start a conversation with someone",
                        style: TextStyle(
                          color: Colors.grey[500],
                        ),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: EdgeInsets.all(16),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    var message = messages[index];
                    return Card(
                      elevation: 2,
                      margin: EdgeInsets.symmetric(vertical: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: ListTile(
                        contentPadding:
                            EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        leading: CircleAvatar(
                          backgroundColor: Color.fromARGB(255, 147, 182, 138),
                          child: Text(
                            message["sender"]["username"]
                                    ?.substring(0, 1)
                                    .toUpperCase() ??
                                "?",
                            style: TextStyle(color: Colors.white),
                          ),
                        ),
                        title: Text(
                          message["sender"]["username"] ?? "Unknown",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(height: 4),
                            Text(
                              message["content"] ?? "No message content",
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: Colors.grey[700],
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              _formatTimestamp(message["timestamp"] ?? ""),
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[500],
                              ),
                            ),
                          ],
                        ),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ChatScreen(
                                senderName: message["sender"]["username"],
                                recipientId: message["sender"]["id"],
                              ),
                            ),
                          ).then((_) => fetchMessages());
                        },
                      ),
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Color.fromARGB(255, 147, 182, 138),
        child: Icon(Icons.message),
        onPressed: () {
          // Implement new message functionality
          // This could navigate to a contacts screen or show a dialog
        },
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    if (timestamp.isEmpty) return "";

    DateTime messageTime = DateTime.parse(timestamp);
    DateTime now = DateTime.now();
    Duration difference = now.difference(messageTime);

    if (difference.inDays > 0) {
      return "${difference.inDays}d ago";
    } else if (difference.inHours > 0) {
      return "${difference.inHours}h ago";
    } else if (difference.inMinutes > 0) {
      return "${difference.inMinutes}m ago";
    } else {
      return "Just now";
    }
  }
}
