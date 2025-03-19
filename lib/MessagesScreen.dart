import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

void main() {
  runApp(MaterialApp(
    home: MessagesScreen(),
  ));
}

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
      body: ListView.builder(
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
        message.message,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Text(
        message.time,
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

class ChatScreen extends StatefulWidget {
  final String senderName;

  ChatScreen({required this.senderName});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];

  // Function to send text messages
  void _sendMessage({String? text, String? filePath}) {
    if ((text?.trim().isNotEmpty ?? false) || (filePath != null)) {
      setState(() {
        _messages.add({
          "text": text,
          "filePath": filePath,
        });
        _messageController.clear();
      });
    }
  }

  // Function to pick a file
  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles();
    if (result != null && result.files.isNotEmpty) {
      String filePath = result.files.first.name; // Display file name
      _sendMessage(filePath: filePath);
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
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                var message = _messages[index];
                return ListTile(
                  title: Align(
                    alignment: Alignment.centerRight,
                    child: Container(
                      padding: EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: message["text"] != null
                            ? Colors.blueAccent
                            : Colors.greenAccent,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: message["text"] != null
                          ? Text(
                        message["text"],
                        style: TextStyle(color: Colors.white),
                      )
                          : Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.attach_file, color: Colors.white),
                          SizedBox(width: 5),
                          Text(
                            message["filePath"],
                            style: TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Row(
              children: [
                IconButton(
                  icon: Icon(Icons.attach_file, color: Colors.blue),
                  onPressed: _pickFile, // Opens file picker
                ),
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: "Type a message...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send, color: Colors.blue),
                  onPressed: () => _sendMessage(text: _messageController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
