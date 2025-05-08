import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:ispani/GroupChatScreen.dart';

class GroupsScreen extends StatefulWidget {
  @override
  _GroupsScreenState createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen> {
  final storage = FlutterSecureStorage();
  List<dynamic> joinedGroups = [];
  List<dynamic> joinableGroups = [];
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    fetchGroups();
  }

  Future<void> fetchGroups() async {
    final token = await storage.read(key: 'access');
    final headers = {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };

    setState(() {
      isLoading = true;
    });

    try {
      final joinedRes = await http.get(
        Uri.parse('http://127.0.0.1:8000/groups/groups/'),
        headers: headers,
      );

      final suggestionsRes = await http.get(
        Uri.parse('http://127.0.0.1:8000/groups/groups/suggestions/'),
        headers: headers,
      );

      if (joinedRes.statusCode == 200 && suggestionsRes.statusCode == 200) {
        setState(() {
          joinedGroups = json.decode(joinedRes.body);
          joinableGroups = json.decode(suggestionsRes.body);
        });
      } else {
        print("Failed to fetch groups.");
      }
    } catch (e) {
      print("Error fetching groups: $e");
    }

    setState(() {
      isLoading = false;
    });
  }

  Future<void> joinGroup(int groupId) async {
    final token = await storage.read(key: 'access');
    final headers = {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };

    setState(() {
      isLoading = true;
    });

    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/groups/groups/$groupId/join/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      await fetchGroups();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Joined group successfully")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to join group")),
      );
    }

    setState(() {
      isLoading = false;
    });
  }

  Future<void> leaveGroup(int groupId) async {
    final token = await storage.read(key: 'access');
    final headers = {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };

    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/groups/$groupId/leave/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      await fetchGroups();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Left group successfully")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to leave group")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text("Groups"),
        backgroundColor: Colors.white,
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView(
              padding: EdgeInsets.all(16),
              children: [
                Text(
                  "Groups you're in",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                SizedBox(height: 10),
                ...joinedGroups.map((group) {
                  return _buildGroupTile(
                    context,
                    title: group['name'] ?? 'Unnamed',
                    subtitle: "You are a member",
                    onLeave: () => leaveGroup(group['id']),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => GroupChatScreen(
                            groupId: group['id'],
                            groupName: group['name'],
                          ),
                        ),
                      );
                    },
                  );
                }).toList(),
                SizedBox(height: 20),
                Text(
                  "Groups you can join",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                SizedBox(height: 10),
                ...joinableGroups.map((group) {
                  return _buildJoinableGroup(
                      context, group['id'], group['name']);
                }).toList(),
              ],
            ),
    );
  }

  Widget _buildGroupTile(
    BuildContext context, {
    required String title,
    required String subtitle,
    VoidCallback? onLeave,
    VoidCallback? onTap,
  }) {
    return Card(
      color: Colors.grey[300],
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey[600],
          child: Icon(Icons.group, color: Colors.white),
        ),
        title: Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: onLeave != null
            ? IconButton(
                icon: Icon(Icons.exit_to_app, color: Colors.red),
                onPressed: onLeave,
              )
            : null,
        onTap: onTap,
      ),
    );
  }

  Widget _buildJoinableGroup(BuildContext context, int groupId, String name) {
    return GestureDetector(
      onTap: () => joinGroup(groupId),
      child: Card(
        color: Colors.grey[200],
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: Colors.grey[600],
            child: Icon(Icons.group_add, color: Colors.white),
          ),
          title: Text(name),
          subtitle: Text("Tap to join"),
          trailing:
              Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[700]),
        ),
      ),
    );
  }
}
