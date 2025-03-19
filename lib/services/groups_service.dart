import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ispani/models.dart';
import 'package:ispani/groupsScreen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Group {
  final int id;
  final String username;
  final String? description;
  final String? lastMessage;
  final String? lastMessageTime;
  final int? unreadCount;
  final bool isMember;
  final String? course;
  final int? yearOfStudy;

  Group({
    required this.id,
    required this.username,
    this.description,
    this.lastMessage,
    this.lastMessageTime,
    this.unreadCount,
    required this.isMember,
    this.course,
    this.yearOfStudy,
  });

  factory Group.fromJson(Map<String, dynamic> json) {
    return Group(
      id: json['id'],
      username: json['name'],
      description: json['description'],
      lastMessage: json['last_message'],
      lastMessageTime: json['last_message_time'],
      unreadCount: json['unread_count'],
      isMember: json['is_member'] ?? false,
      course: json['course'],
      yearOfStudy: json['year_of_study'],
    );
  }
}

class GroupsService {
  static const String baseUrl = 'http://127.0.0.1:8000/groups/'; // Replace with your actual API URL
  
  // Get token from shared preferences
  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  // Get all groups the user is in
  static Future<List<Group>> getUserGroups() async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/groups/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> groupsJson = jsonDecode(response.body);
      List<Group> allGroups = groupsJson.map((json) => Group.fromJson(json)).toList();
      
      // Filter for groups where the user is a member
      return allGroups.where((group) => group.isMember).toList();
    } else {
      throw Exception('Failed to load user groups: ${response.statusCode}');
    }
  }

  // Get groups the user can join
  static Future<List<Group>> getJoinableGroups() async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/groups/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> groupsJson = jsonDecode(response.body);
      List<Group> allGroups = groupsJson.map((json) => Group.fromJson(json)).toList();
      
      // Filter for groups where the user is not a member
      return allGroups.where((group) => !group.isMember).toList();
    } else {
      throw Exception('Failed to load joinable groups: ${response.statusCode}');
    }
  }

  // Join a group
  static Future<bool> joinGroup(int groupId) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/join-group/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'group_id': groupId,
      }),
    );

    return response.statusCode == 200;
  }

  // Get special group types
  static Future<List<Group>> getSpecialGroups(String type) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');
    
    String endpoint;
    if (type == 'study') {
      endpoint = '$baseUrl/study-groups/';
    } else if (type == 'hobby') {
      endpoint = '$baseUrl/hobby-groups/';
    } else {
      throw Exception('Invalid group type');
    }

    final response = await http.get(
      Uri.parse(endpoint),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> groupsJson = jsonDecode(response.body);
      return groupsJson.map((json) => Group.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load $type groups: ${response.statusCode}');
    }
  }

// Get messages for a group
  static Future<List<Message>> getGroupMessages(int groupId) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/groups/$groupId/messages/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> messagesJson = jsonDecode(response.body);
      return messagesJson.map((json) => Message.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load messages: ${response.statusCode}');
    }
  }

  // Send a message to a group
  static Future<bool> sendMessage(int groupId, String content) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/messages/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'group': groupId,
        'content': content,
      }),
    );

    return response.statusCode == 201;
  }

  // Leave a group
  static Future<bool> leaveGroup(int groupId) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/leave-group/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'group_id': groupId,
      }),
    );

    return response.statusCode == 200;
  }

  // Create a new group
  static Future<Group> createGroup({
    required String name,
    String? description,
    String? course,
    int? yearOfStudy,
  }) async {
    final token = await _getToken();
    if (token == null) throw Exception('Not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/groups/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'name': name,
        'description': description,
        'course': course,
        'year_of_study': yearOfStudy,
      }),
    );

    if (response.statusCode == 201) {
      Map<String, dynamic> groupJson = jsonDecode(response.body);
      return Group.fromJson(groupJson);
    } else {
      throw Exception('Failed to create group: ${response.statusCode}');
    }
  }

}