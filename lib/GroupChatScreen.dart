import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class GroupChatScreen extends StatefulWidget {
  final int groupId;
  final String groupName;

  GroupChatScreen({
    required this.groupId,
    required this.groupName,
  });

  @override
  _GroupChatScreenState createState() => _GroupChatScreenState();
}

class _GroupChatScreenState extends State<GroupChatScreen> {
  late WebSocketChannel channel;
  final TextEditingController _controller = TextEditingController();
  List<Map<String, String>> messages = [];

  @override
  void initState() {
    super.initState();
    channel = IOWebSocketChannel.connect(
      Uri.parse("ws://127.0.0.1:8000/ws/groupchat/${widget.groupId}/"),
    );

    channel.stream.listen((data) {
      final decoded = jsonDecode(data);
      setState(() {
        messages.add({
          'username': decoded['username'],
          'message': decoded['message'],
        });
      });
    });
  }

  void sendMessage() {
    if (_controller.text.isNotEmpty) {
      final msg = {
        'username': 'Ntando',
        'message': _controller.text,
      };
      channel.sink.add(jsonEncode(msg));
      _controller.clear();
    }
  }

  @override
  void dispose() {
    channel.sink.close();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.groupName)),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: EdgeInsets.all(8),
              children: messages.map((msg) {
                return ListTile(
                  title: Text(msg['username'] ?? ''),
                  subtitle: Text(msg['message'] ?? ''),
                );
              }).toList(),
            ),
          ),
          Divider(height: 1),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: "Enter message...",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send, color: Colors.blue),
                  onPressed: sendMessage,
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
