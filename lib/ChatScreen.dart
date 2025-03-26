import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class ChatScreen extends StatefulWidget {
  final String senderName;
  final int recipientId;

  ChatScreen({required this.senderName, required this.recipientId});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  List<dynamic> messages = [];
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchChatHistory();
  }

  Future<void> fetchChatHistory() async {
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
        Uri.parse(
            "http://127.0.0.1:8000/messages/private/inbox/${widget.recipientId}/"),
        headers: {"Authorization": "Bearer $token"},
      );

      if (response.statusCode == 200) {
        setState(() {
          messages = json.decode(response.body);
          isLoading = false;
        });

        // Scroll to bottom after messages load
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
        });
      } else {
        print("Failed to load chat history");
        setState(() {
          isLoading = false;
        });
      }
    } catch (error) {
      print("Error fetching chat history: $error");
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    String content = _messageController.text;
    _messageController.clear();

    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? token = prefs.getString("access_token");

    if (token == null) {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please log in to send messages")));
      return;
    }

    try {
      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/messages/private/"),
        body: jsonEncode(
            {"recipient_id": widget.recipientId, "content": content}),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token"
        },
      );

      if (response.statusCode == 201) {
        fetchChatHistory(); // Refresh messages
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Failed to send message")));
      }
    } catch (error) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Error: $error")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              backgroundColor: Color.fromARGB(255, 147, 182, 138),
              child: Text(
                widget.senderName.isNotEmpty
                    ? widget.senderName[0].toUpperCase()
                    : "?",
                style: TextStyle(color: Colors.white),
              ),
            ),
            SizedBox(width: 10),
            Text(
              widget.senderName,
              style: TextStyle(
                color: Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.more_vert, color: Colors.black),
            onPressed: () {
              // Show chat options
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: isLoading
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
                            Icon(Icons.chat_bubble_outline,
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
                              "Send a message to start the conversation",
                              style: TextStyle(
                                color: Colors.grey[500],
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollController,
                        padding: EdgeInsets.all(16),
                        itemCount: messages.length,
                        itemBuilder: (context, index) {
                          var message = messages[index];
                          bool isMe =
                              message["sender"]["id"] != widget.recipientId;

                          return Align(
                            alignment: isMe
                                ? Alignment.centerRight
                                : Alignment.centerLeft,
                            child: Container(
                              margin: EdgeInsets.symmetric(vertical: 6),
                              padding: EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 10),
                              decoration: BoxDecoration(
                                color: isMe
                                    ? Color.fromARGB(255, 147, 182, 138)
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(18),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.05),
                                    blurRadius: 3,
                                    offset: Offset(0, 1),
                                  ),
                                ],
                              ),
                              constraints: BoxConstraints(
                                maxWidth:
                                    MediaQuery.of(context).size.width * 0.75,
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    message["content"],
                                    style: TextStyle(
                                      color:
                                          isMe ? Colors.white : Colors.black87,
                                      fontSize: 16,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    _formatTimestamp(
                                        message["timestamp"] ?? ""),
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: isMe
                                          ? Colors.white.withOpacity(0.8)
                                          : Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 3,
                  offset: Offset(0, -1),
                ),
              ],
            ),
            child: Row(
              children: [
                IconButton(
                  icon: Icon(Icons.attach_file),
                  color: Colors.grey[700],
                  onPressed: () {
                    // Handle attachments
                  },
                ),
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: "Type a message...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.grey[200],
                      contentPadding:
                          EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                    textCapitalization: TextCapitalization.sentences,
                    minLines: 1,
                    maxLines: 5,
                  ),
                ),
                SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: Color.fromARGB(255, 147, 182, 138),
                  child: IconButton(
                    icon: Icon(Icons.send),
                    color: Colors.white,
                    onPressed: sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    if (timestamp.isEmpty) return "";

    DateTime messageTime = DateTime.parse(timestamp);
    DateTime now = DateTime.now();

    // Same day, show time only
    if (messageTime.year == now.year &&
        messageTime.month == now.month &&
        messageTime.day == now.day) {
      return "${messageTime.hour.toString().padLeft(2, '0')}:${messageTime.minute.toString().padLeft(2, '0')}";
    }

    // This week, show day of week
    if (now.difference(messageTime).inDays < 7) {
      List<String> weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return "${weekdays[messageTime.weekday - 1]} ${messageTime.hour.toString().padLeft(2, '0')}:${messageTime.minute.toString().padLeft(2, '0')}";
    }

    // Older, show date
    return "${messageTime.day}/${messageTime.month}/${messageTime.year}";
  }
}
