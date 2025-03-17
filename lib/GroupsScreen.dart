import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html; // For web storage fallback
import 'package:ispani/Login.dart';
import 'package:flutter/foundation.dart';

class GroupsScreen extends StatefulWidget {
  @override
  _GroupsScreenState createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen> {
  bool isLoading = true;
  List<dynamic> myGroups = [];
  List<dynamic> joinableGroups = [];
  Map<String, dynamic> announcements = {};

  final FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  static final bool _isWeb = kIsWeb; // Web detection

  static const String baseUrl = "http://127.0.0.1:8000";

  @override
  void initState() {
    super.initState();
    _fetchGroups();
  }

  // Retrieve access token from storage (Web or mobile)
  Future<String> getAccessToken() async {
    String token;
    if (_isWeb) {
      token = html.window.localStorage['access_token'] ?? '';
    } else {
      token = await _secureStorage.read(key: 'access_token') ?? '';
    }
    print('Retrieved token: $token'); // Debugging line to verify token retrieval
    return token;
  }

  // Retrieve user ID from storage (Web or mobile)
  Future<String> getUserId() async {
    String userId;
    if (_isWeb) {
      userId = html.window.localStorage['user_id'] ?? '';
    } else {
      userId = await _secureStorage.read(key: 'user_id') ?? '';
    }
    print('Retrieved userId: $userId'); // Debugging line to verify userId retrieval
    return userId;
  }

  // Check if the user is authenticated by validating the token
  Future<bool> _checkAuthentication() async {
    final token = await getAccessToken();
    if (token.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('You are not logged in. Please log in first.')),
        );
      }
      return false;
    }
    return true;
  }

  // Fetch groups and announcements from the backend
  Future<void> _fetchGroups() async {
    if (!await _checkAuthentication()) return;

    final accessToken = await getAccessToken();
    final userId = await getUserId();

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/groups/'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final allGroups = json.decode(response.body);

        final List<dynamic> myGroupsList = [];
        final List<dynamic> joinableGroupsList = [];

        for (var group in allGroups) {
          bool isMember = group['members']?.any((member) => member['id'] == int.tryParse(userId)) ?? false;
          isMember ? myGroupsList.add(group) : joinableGroupsList.add(group);
        }

        final announcementsResponse = await http.get(
          Uri.parse('$baseUrl/groups/announcements/'),
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        );

        if (announcementsResponse.statusCode == 200) {
          setState(() {
            myGroups = myGroupsList;
            joinableGroups = joinableGroupsList;
            announcements = json.decode(announcementsResponse.body);
            isLoading = false;
          });
        }
      } else if (response.statusCode == 401) {
        // Token expired, refresh the token
        await _handleTokenRefresh();
        _fetchGroups(); // Retry request
      } else {
        _handleFetchError(response.statusCode, response.body);
      }
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  // Handle token refresh if expired
  Future<void> _handleTokenRefresh() async {
    final refreshToken = await _secureStorage.read(key: 'refresh_token') ?? '';

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final newTokens = json.decode(response.body);
        await _secureStorage.write(key: 'access_token', value: newTokens['access']);
      } else {
        await _secureStorage.deleteAll();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Session expired, please log in again')),
          );
        }
      }
    } catch (e) {
      await _secureStorage.deleteAll();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Session expired, please log in again')),
        );
      }
    }
  }

  // Handle fetch errors
  void _handleFetchError(int statusCode, String responseBody) {
    print('Failed to load groups: $statusCode');
    print('Response Body: $responseBody');

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load groups: $statusCode')),
      );
    }

    setState(() => isLoading = false);
  }

  // Handle network errors
  void _handleNetworkError(dynamic e) {
    print('Network error fetching groups: $e');

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Network error: ${e.toString()}')),
      );
    }

    setState(() => isLoading = false);
  }

  // Request to join a group
  Future<void> _requestToJoinGroup(int groupId) async {
    if (!await _checkAuthentication()) return;

    try {
      final token = await getAccessToken();
      final response = await http.post(
        Uri.parse("$baseUrl/groups/$groupId/join/"),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final responseBody = json.decode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(responseBody['message'] ?? 'Successfully joined group')),
          );
        }
        _fetchGroups();
      } else {
        _handleJoinError(response);
      }
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  // Handle join group errors
  void _handleJoinError(http.Response response) {
    final responseData = json.decode(response.body);
    print('Failed to join group: ${responseData['message'] ?? 'Unknown error'}');

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to join group: ${responseData['message'] ?? 'Unknown error'}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Groups"),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _fetchGroups,
          ),
        ],
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _fetchGroups,
              child: ListView(
                padding: EdgeInsets.all(16),
                children: [
                  _buildGroupTile(
                    title: "Announcements",
                    subtitle: announcements['latest_message'] ?? "No recent announcements",
                  ),
                  Text("Groups you're in"),
                  if (myGroups.isEmpty)
                    Text("You are not a member of any groups yet.")
                  else
                    ...myGroups.map((group) => _buildGroupTile(title: group['name'])),
                ],
              ),
            ),
    );
  }

  // Build the group tile widget
  Widget _buildGroupTile({required String title, String subtitle = ""}) {
    return ListTile(
      title: Text(title),
      subtitle: Text(subtitle),
    );
  }
}
