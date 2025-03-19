import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class GroupsScreen extends StatefulWidget {
  @override
  _GroupsScreenState createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen> {
  List<dynamic> groups = [];
  final String apiUrl = "http://127.0.0.1:8000/groups/";

  @override
  void initState() {
    super.initState();
    fetchGroups();
  }

  Future<void> fetchGroups() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        setState(() {
          groups = json.decode(response.body);
        });
      } else {
        print("Failed to load groups");
      }
    } catch (error) {
      print("Error fetching groups: $error");
    }
  }

  Future<void> joinGroup(int groupId) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  String? token = prefs.getString("access_token");

  if (token == null) {
    print("No authentication token found.");
    return;
  }

    final response = await http.post(
      Uri.parse("http://127.0.0.1:8000/join-group/"),
      body: jsonEncode({"group_id": groupId}),
      headers:{
              "Content-Type": "application/json",
             "Authorization": "Bearer $token"
             },
    );

    if (response.statusCode == 200) {
      print("Joined group successfully");
      fetchGroups(); // Refresh list
    } else {
      print("Failed to join group");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Groups")),
      body: ListView.builder(
        itemCount: groups.length,
        itemBuilder: (context, index) {
          var group = groups[index];
          return ListTile(
            title: Text(group["name"]),
            subtitle: Text(group["description"] ?? "No description"),
            trailing: IconButton(
              icon: Icon(Icons.group_add),
              onPressed: () => joinGroup(group["id"]),
            ),
          );
        },
      ),
    );
  }
}
