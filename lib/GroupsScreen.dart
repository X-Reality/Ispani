import 'package:flutter/material.dart';

class GroupsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // Light grey background
      appBar: AppBar(
        title: Text("Groups"),
        backgroundColor: Colors.white, // Darker grey for the AppBar
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          // Announcements Card
          _buildGroupTile(
            context,
            title: "Announcements",
            subtitle: "~ Ntsako Mgiba: Photo",
            trailing: Text("53", style: TextStyle(color: Colors.green)),
            date: "2025/02/13",
            icon: Icons.campaign_outlined,
          ),
          SizedBox(height: 20),
          Text(
            "Groups you're in",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          _buildGroupTile(
            context,
            title: "Founders Only 🔧",
            subtitle: "~ Vanessa Perumal: Thank you for the...",
            time: "14:01",
          ),
          SizedBox(height: 20),
          Text(
            "Groups you can join",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          _buildJoinableGroup(context, "DIT Opportunity Hub 🚨"),
          _buildJoinableGroup(context, "DIT AI Fanatics 🤖"),
          _buildJoinableGroup(context, "Social Media Support Circle 🤝"),
          _buildJoinableGroup(context, "The Jobs Board 📸📋"),
          _buildJoinableGroup(context, "The Press Plug 📰🛠️"),
        ],
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
      ),
    );
  }

  Widget _buildJoinableGroup(BuildContext context, String groupName) {
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
      ),
    );
  }
}
