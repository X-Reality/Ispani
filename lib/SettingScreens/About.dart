import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({Key? key}) : super(key: key);

  final String appName = "Ispani";
  final String version = "v1.0.0";
  final String company = "Ispani PTY LTD.";
  final String description = "UpTransfer is a modern platform that helps you manage your tutoring sessions, bookings, and learning progress — all in one place.";
  final String copyright = "© 2025 ISpani. All rights reserved.";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("About")),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            /// Optional logo
            const SizedBox(height: 30),
            Image.asset('assets/logo2.1.jpg'),

            const SizedBox(height: 20),
            Text("Ispani",
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(version, style: const TextStyle(color: Colors.grey)),

            const SizedBox(height: 20),
            Text(
              description,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge,
            ),

            const Spacer(),
            Divider(),
            Text(company, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(
              copyright,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
