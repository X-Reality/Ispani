import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class GroupsScreen extends StatefulWidget {
  @override
  _GroupsScreenState createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen> {
  bool isLoading = true;
  List<dynamic> myGroups = [];
  List<dynamic> joinableGroups = [];
  Map<String, dynamic> announcements = {};

  @override
  void initState() {
    super.initState();
    _fetchGroups();
  }

  Future<void> _fetchGroups() async {
    setState(() {
      isLoading = true;
    });

    try {
      // Get groups the user is a member of
      final myGroupsResponse = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/my-groups/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token storage
        },
      );

      // Get groups the user can join
      final joinableGroupsResponse = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/joinable-groups/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token storage
        },
      );

      // Get announcements
      final announcementsResponse = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/announcements/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token storage
        },
      );

      if (myGroupsResponse.statusCode == 200 && 
          joinableGroupsResponse.statusCode == 200 && 
          announcementsResponse.statusCode == 200) {
        setState(() {
          myGroups = json.decode(myGroupsResponse.body);
          joinableGroups = json.decode(joinableGroupsResponse.body);
          announcements = json.decode(announcementsResponse.body);
          isLoading = false;
        });
      } else {
        // Handle error
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load groups')),
        );
        setState(() {
          isLoading = false;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Network error: ${e.toString()}')),
      );
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> _requestToJoinGroup(int groupId) async {
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/join-group/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token storage
        },
        body: json.encode({
          'group_id': groupId,
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Join request sent successfully')),
        );
        // Refresh the groups
        _fetchGroups();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send join request')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Network error: ${e.toString()}')),
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
        : RefreshIndicator(
            onRefresh: _fetchGroups,
            child: ListView(
              padding: EdgeInsets.all(16),
              children: [
                // Announcements Card
                _buildGroupTile(
                  context,
                  title: "Announcements",
                  subtitle: announcements['latest_message'] ?? "No recent announcements",
                  trailing: Text(
                    announcements['unread_count']?.toString() ?? "0", 
                    style: TextStyle(color: Colors.green)
                  ),
                  date: announcements['latest_date'] ?? "",
                  icon: Icons.campaign_outlined,
                ),
                SizedBox(height: 20),
                Text(
                  "Groups you're in",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                if (myGroups.isEmpty)
                  Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text("You are not a member of any groups yet."),
                  )
                else
                  ...myGroups.map((group) => _buildGroupTile(
                    context,
                    title: group['name'] ?? "Unknown Group",
                    subtitle: group['latest_message'] ?? "No messages yet",
                    time: group['latest_time'] ?? "",
                    onTap: () {
                      // Navigate to group detail/chat screen
                      // Navigator.push(...);
                    },
                  )),
                SizedBox(height: 20),
                Text(
                  "Groups you can join",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                if (joinableGroups.isEmpty)
                  Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text("No groups available to join."),
                  )
                else
                  ...joinableGroups.map((group) => _buildJoinableGroup(
                    context, 
                    group['name'] ?? "Unknown Group",
                    groupId: group['id'],
                  )),
              ],
            ),
          ),
    );
  }

  Widget _buildGroupTile(
    BuildContext context, {
    required String title,
    required String subtitle,
    String? time,
    String? date,
    Widget? trailing,
    IconData? icon,
    Function()? onTap,
  }) {
    return Card(
      color: Colors.grey[300],
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey[600],
          child: Icon(icon ?? Icons.group, color: Colors.white),
        ),
        title: Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (date != null)
              Text(date, style: TextStyle(color: Colors.green, fontSize: 12)),
            if (time != null)
              Text(time, style: TextStyle(color: Colors.grey[700], fontSize: 12)),
            if (trailing != null) trailing,
          ],
        ),
        onTap: onTap,
      ),
    );
  }

  Widget _buildJoinableGroup(BuildContext context, String groupName, {required int groupId}) {
    return Card(
      color: Colors.grey[300],
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey[600],
          child: Icon(Icons.group_add, color: Colors.white),
        ),
        title: Text(groupName),
        subtitle: Text("Request to join"),
        trailing: Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[700]),
        onTap: () => _requestToJoinGroup(groupId),
      ),
    );
  }
}