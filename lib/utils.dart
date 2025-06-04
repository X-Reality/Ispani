import 'package:flutter/material.dart';

Widget buildPlaceholderScreen(BuildContext context, String title) {
  return Scaffold(
    appBar: AppBar(
      title: Text(title, style: const TextStyle(color: Colors.black)),
      backgroundColor: Colors.white,
      iconTheme: const IconThemeData(color: Colors.black),
      elevation: 0.5,
    ),
    body: Center(
      child: Text(
        "$title screen coming soon",
        style: const TextStyle(fontSize: 16),
      ),
    ),
  );
}
