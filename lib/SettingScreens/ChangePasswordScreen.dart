import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class ChangePasswordScreen extends StatelessWidget {
  const ChangePasswordScreen({super.key});

  Future<void> _launchURL() async {
    final Uri url = Uri.parse('https://xrlab.co.za');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Change Password")),
      body: Center(
        child: ElevatedButton(
          onPressed: _launchURL,
          child: const Text("Go to Change Password Page"),
        ),
      ),
    );
  }
}
