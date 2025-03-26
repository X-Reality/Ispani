import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class GroupsScreen extends StatefulWidget {
  @override
  _GroupsScreenState createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen>
    with SingleTickerProviderStateMixin {
  List<dynamic> studyGroups = [];
  List<dynamic> hobbyGroups = [];
  final String apiBaseUrl = "http://127.0.0.1:8000/";
  bool isLoading = true;
  late TabController _tabController;
  String? token;

  // App theme color
  final Color primaryGreen = Color.fromARGB(255, 147, 182, 138);

  // Colors for course and year text
  final Color courseTextColor =
      Color.fromARGB(255, 67, 122, 61); // Darker forest green
  final Color yearTextColor = Color.fromARGB(255, 95, 125, 50); // Olive green

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadToken();
  }

  @override
  void dispose() {
    _tabController.dispose();
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
          SnackBar(content: Text("Please log in to view groups")));
    } else {
      fetchGroups();
    }
  }

  Future<void> fetchGroups() async {
    if (token == null) {
      setState(() {
        isLoading = false;
      });
      return;
    }

    try {
      // Fetch study groups with authentication
      final studyResponse = await http.get(
        Uri.parse("${apiBaseUrl}study-groups/"),
        headers: {"Authorization": "Bearer $token"},
      );

      // Fetch hobby groups with authentication
      final hobbyResponse = await http.get(
        Uri.parse("${apiBaseUrl}hobby-groups/"),
        headers: {"Authorization": "Bearer $token"},
      );

      if (studyResponse.statusCode == 200 && hobbyResponse.statusCode == 200) {
        setState(() {
          studyGroups = json.decode(studyResponse.body);
          hobbyGroups = json.decode(hobbyResponse.body);
          isLoading = false;
        });
      } else {
        print(
            "Failed to load groups: Study status: ${studyResponse.statusCode}, Hobby status: ${hobbyResponse.statusCode}");
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("Failed to load groups. Please try again.")));
      }
    } catch (error) {
      print("Error fetching groups: $error");
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error loading groups: $error")));
    }
  }

  Future<void> joinGroup(int groupId) async {
    if (token == null) {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please log in to join a group")));
      return;
    }

    try {
      final response = await http.post(
        Uri.parse("${apiBaseUrl}join-group/"),
        body: jsonEncode({"group_id": groupId}),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token"
        },
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Joined group successfully")));
        fetchGroups(); // Refresh list
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Failed to join group")));
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
        title: Text(
          "Groups",
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
        bottom: TabBar(
          controller: _tabController,
          labelColor: primaryGreen,
          unselectedLabelColor: Colors.grey,
          indicatorColor: primaryGreen,
          tabs: [
            Tab(text: "Study Groups"),
            Tab(text: "Hobby Groups"),
          ],
        ),
      ),
      body: isLoading
          ? Center(
              child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(primaryGreen),
            ))
          : token == null
              ? _buildLoginPrompt()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildGroupsList(studyGroups),
                    _buildGroupsList(hobbyGroups),
                  ],
                ),
      floatingActionButton: token == null
          ? null
          : FloatingActionButton(
              backgroundColor: primaryGreen,
              child: Icon(Icons.add),
              onPressed: () {
                _showCreateGroupDialog();
              },
            ),
    );
  }

  Widget _buildLoginPrompt() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.lock_outline, size: 70, color: Colors.grey[400]),
          SizedBox(height: 16),
          Text(
            "Authentication Required",
            style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500),
          ),
          SizedBox(height: 8),
          Text(
            "Please log in to view and join groups",
            style: TextStyle(
              color: Colors.grey[500],
            ),
          ),
          SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: primaryGreen,
              padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            child: Text("Log In"),
            onPressed: () {
              // Navigate to login screen
              // Navigator.of(context).pushNamed('/login');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildGroupsList(List<dynamic> groups) {
    if (groups.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.group_outlined, size: 70, color: Colors.grey[400]),
            SizedBox(height: 16),
            Text(
              "No groups available",
              style: TextStyle(
                  fontSize: 18,
                  color: Colors.grey[600],
                  fontWeight: FontWeight.w500),
            ),
            SizedBox(height: 8),
            Text(
              "Create a new group to get started",
              style: TextStyle(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: EdgeInsets.all(16),
      itemCount: groups.length,
      itemBuilder: (context, index) {
        var group = groups[index];
        return Card(
          elevation: 2,
          margin: EdgeInsets.symmetric(vertical: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        group["name"],
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ),
                    Container(
                      decoration: BoxDecoration(
                        color: primaryGreen.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding:
                          EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      child: Text(
                        "${group["members_count"] ?? 0} members",
                        style: TextStyle(
                          color: primaryGreen,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                if (group["description"] != null &&
                    group["description"].toString().isNotEmpty)
                  Text(
                    group["description"],
                    style: TextStyle(color: Colors.grey[700]),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                SizedBox(height: 12),

                // New design for course and year information
                Row(
                  children: [
                    if (group["course"] != null &&
                        group["course"].toString().isNotEmpty) ...[
                      Icon(Icons.book, size: 16, color: courseTextColor),
                      SizedBox(width: 4),
                      Text(
                        group["course"],
                        style: TextStyle(
                          color: courseTextColor,
                          fontWeight: FontWeight.w500,
                          fontSize: 13,
                        ),
                      ),
                      SizedBox(width: 16),
                    ],
                    if (group["year_of_study"] != null) ...[
                      Icon(Icons.calendar_today,
                          size: 16, color: yearTextColor),
                      SizedBox(width: 4),
                      Text(
                        "Year ${group["year_of_study"]}",
                        style: TextStyle(
                          color: yearTextColor,
                          fontWeight: FontWeight.w500,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ],
                ),

                SizedBox(height: 16),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton.icon(
                    icon: Icon(Icons.group_add),
                    label: Text("Join"),
                    style: ElevatedButton.styleFrom(
                      foregroundColor: Colors.white,
                      backgroundColor: primaryGreen,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    onPressed: () => joinGroup(group["id"]),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showCreateGroupDialog() {
    final nameController = TextEditingController();
    final descriptionController = TextEditingController();
    String groupType = "STUDY";
    String? course;
    String? yearOfStudy;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text("Create New Group"),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: nameController,
                  decoration: InputDecoration(
                    labelText: "Group Name",
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: descriptionController,
                  maxLines: 3,
                  decoration: InputDecoration(
                    labelText: "Description",
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                Text("Group Type:"),
                Row(
                  children: [
                    Radio(
                      value: "STUDY",
                      groupValue: groupType,
                      onChanged: (value) {
                        setDialogState(() {
                          groupType = value.toString();
                        });
                      },
                      activeColor: primaryGreen,
                    ),
                    Text("Study"),
                    Radio(
                      value: "HOBBY",
                      groupValue: groupType,
                      onChanged: (value) {
                        setDialogState(() {
                          groupType = value.toString();
                        });
                      },
                      activeColor: primaryGreen,
                    ),
                    Text("Hobby"),
                  ],
                ),
                if (groupType == "STUDY") ...[
                  SizedBox(height: 16),
                  TextField(
                    decoration: InputDecoration(
                      labelText: "Course",
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.book, color: courseTextColor),
                    ),
                    onChanged: (value) {
                      course = value;
                    },
                  ),
                  SizedBox(height: 16),
                  TextField(
                    decoration: InputDecoration(
                      labelText: "Year of Study",
                      border: OutlineInputBorder(),
                      prefixIcon:
                          Icon(Icons.calendar_today, color: yearTextColor),
                    ),
                    keyboardType: TextInputType.number,
                    onChanged: (value) {
                      yearOfStudy = value;
                    },
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              child: Text("Cancel"),
              onPressed: () => Navigator.pop(context),
            ),
            ElevatedButton(
              child: Text("Create"),
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryGreen,
              ),
              onPressed: () async {
                if (nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text("Group name is required")));
                  return;
                }

                Navigator.pop(context);

                // Show loading indicator
                ScaffoldMessenger.of(context)
                    .showSnackBar(SnackBar(content: Text("Creating group...")));

                try {
                  Map<String, dynamic> requestBody = {
                    "name": nameController.text,
                    "description": descriptionController.text,
                    "type": groupType,
                  };

                  if (groupType == "STUDY") {
                    if (course != null) requestBody["course"] = course;
                    if (yearOfStudy != null)
                      requestBody["year_of_study"] = int.tryParse(yearOfStudy!);
                  }

                  final response = await http.post(
                    Uri.parse("${apiBaseUrl}create-group/"),
                    body: jsonEncode(requestBody),
                    headers: {
                      "Content-Type": "application/json",
                      "Authorization": "Bearer $token"
                    },
                  );

                  if (response.statusCode == 201) {
                    ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Group created successfully")));
                    fetchGroups(); // Refresh the list
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Failed to create group")));
                  }
                } catch (error) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text("Error: $error")));
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
