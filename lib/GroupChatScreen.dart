import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:async';

class GroupChatScreen extends StatefulWidget {
  final int groupId;
  final String groupName;

  GroupChatScreen({required this.groupId, required this.groupName});

  @override
  _GroupChatScreenState createState() => _GroupChatScreenState();
}

class _GroupChatScreenState extends State<GroupChatScreen> {
  List<dynamic> messages = [];
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final String apiBaseUrl = "http://127.0.0.1:8000/";
  bool isLoading = true;
  String? token;
  Timer? _messageRefreshTimer;
  final Color primaryGreen = Color.fromARGB(255, 147, 182, 138);

  @override
  void initState() {
    super.initState();
    _loadToken();

    // Set up periodic message refresh (every 5 seconds)
    _messageRefreshTimer = Timer.periodic(Duration(seconds: 5), (timer) {
      fetchMessages();
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _messageRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    token = prefs.getString("access_token");

    if (token == null) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please log in to view messages")));
    } else {
      fetchMessages();
    }
  }

  Future<void> fetchMessages() async {
    if (token == null) {
      setState(() {
        isLoading = false;
      });
      return;
    }

    try {
      final response = await http.get(
        Uri.parse("${apiBaseUrl}groups/${widget.groupId}/messages/"),
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
        print("Failed to load messages: ${response.statusCode}");
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("Failed to load messages. Please try again.")));
      }
    } catch (error) {
      print("Error fetching messages: $error");
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error loading messages: $error")));
    }
  }

  Future<void> sendMessage() async {
    if (token == null) {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please log in to send messages")));
      return;
    }

    final messageText = _messageController.text.trim();
    if (messageText.isEmpty) return;

    try {
      final response = await http.post(
        Uri.parse("${apiBaseUrl}messages/"),
        body: jsonEncode({
          "content": messageText,
          "group_id": widget.groupId,
        }),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token"
        },
      );

      if (response.statusCode == 201) {
        // Clear the text field
        _messageController.clear();

        // Fetch latest messages
        fetchMessages();
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
      appBar: AppBar(
        title: Text(
          widget.groupName,
          style: TextStyle(
            color: Colors.black,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        iconTheme: IconThemeData(color: Colors.black),
        actions: [
          IconButton(
            icon: Icon(Icons.info_outline),
            onPressed: () {
              // Show group info dialog
              _showGroupInfoDialog();
            },
          ),
        ],
      ),
      body: isLoading
          ? Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(primaryGreen),
              ),
            )
          : Column(
              children: [
                Expanded(
                  child: messages.isEmpty
                      ? _buildEmptyMessageView()
                      : ListView.builder(
                          controller: _scrollController,
                          padding: EdgeInsets.all(16),
                          itemCount: messages.length,
                          itemBuilder: (context, index) {
                            return _buildMessageItem(messages[index]);
                          },
                        ),
                ),
                _buildMessageComposer(),
              ],
            ),
    );
  }

  Widget _buildEmptyMessageView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.chat_bubble_outline, size: 70, color: Colors.grey[400]),
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
            "Start the conversation!",
            style: TextStyle(
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageItem(dynamic message) {
    final bool isMyMessage = message["sender"]["username"] ==
        "currentUser"; // You'll need to get current username

    return Align(
      alignment: isMyMessage ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 8),
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isMyMessage ? primaryGreen : Colors.grey[200],
          borderRadius: BorderRadius.circular(18),
        ),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isMyMessage)
              Text(
                message["sender"]["username"] ?? "Unknown",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  color: isMyMessage ? Colors.white70 : Colors.grey[700],
                ),
              ),
            SizedBox(height: !isMyMessage ? 4 : 0),
            Text(
              message["content"],
              style: TextStyle(
                color: isMyMessage ? Colors.white : Colors.black,
              ),
            ),
            SizedBox(height: 4),
            Text(
              _formatTimestamp(message["timestamp"]),
              style: TextStyle(
                fontSize: 10,
                color: isMyMessage ? Colors.white70 : Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    DateTime dateTime = DateTime.parse(timestamp);
    return "${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}";
  }

  Widget _buildMessageComposer() {
    return Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            offset: Offset(0, -1),
            blurRadius: 5,
            color: Colors.black.withOpacity(0.06),
          ),
        ],
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(Icons.attach_file),
            color: Colors.grey[600],
            onPressed: () {
              // Handle file attachment
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
                fillColor: Colors.grey[100],
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              maxLines: null,
              textCapitalization: TextCapitalization.sentences,
            ),
          ),
          SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: primaryGreen,
            child: IconButton(
              icon: Icon(Icons.send),
              color: Colors.white,
              onPressed: sendMessage,
            ),
          ),
        ],
      ),
    );
  }

  void _showGroupInfoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text("Group Info"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.groupName,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
            SizedBox(height: 16),
            // You can fetch and display more group info here
            Text("Group ID: ${widget.groupId}"),
            // Add more details like member count, etc.
          ],
        ),
        actions: [
          TextButton(
            child: Text("Close"),
            onPressed: () => Navigator.pop(context),
          ),
          TextButton(
            child: Text("Leave Group"),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            onPressed: () {
              // Implement leave group functionality
              Navigator.pop(context);
              _leaveGroup();
            },
          ),
        ],
      ),
    );
  }

  Future<void> _leaveGroup() async {
    if (token == null) return;

    try {
      final response = await http.post(
        Uri.parse("${apiBaseUrl}leave-group/"),
        body: jsonEncode({"group_id": widget.groupId}),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token"
        },
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("You have left the group")));
        Navigator.pop(context); // Go back to groups screen
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Failed to leave group")));
      }
    } catch (error) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Error: $error")));
    }
  }
}
