import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ResetPasswordConfirm extends StatefulWidget {
  final String uid;
  final String token;

  const ResetPasswordConfirm({
    super.key,
    required this.uid,
    required this.token,
  });

  @override
  State<ResetPasswordConfirm> createState() => _ResetPasswordConfirmState();
}

class _ResetPasswordConfirmState extends State<ResetPasswordConfirm> {
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _loading = false;

  void _showDialog(String message, {bool success = false}) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(success ? "Success" : "Error"),
        content: Text(message),
        actions: [
          TextButton(
            child: Text("OK"),
            onPressed: () {
              Navigator.of(context).pop();
              if (success) Navigator.of(context).pop(); // Go back on success
            },
          ),
        ],
      ),
    );
  }

  Future<void> _resetPassword() async {
    final newPassword = _newPasswordController.text.trim();
    final confirmPassword = _confirmPasswordController.text.trim();

    if (newPassword.isEmpty || confirmPassword.isEmpty) {
      _showDialog("Please fill in all fields.");
      return;
    }

    if (newPassword != confirmPassword) {
      _showDialog("Passwords do not match.");
      return;
    }

    setState(() => _loading = true);

    try {
      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/auth/reset-password/"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "uid": widget.uid,
          "token": widget.token,
          "new_password": newPassword,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _showDialog(data['message'] ?? "Password reset successful!",
            success: true);
      } else {
        _showDialog(data['error'] ?? "Invalid or expired link.");
      }
    } catch (e) {
      _showDialog("Network error. Try again.");
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Reset Your Password")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: _newPasswordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: "New Password",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _confirmPasswordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: "Confirm Password",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loading ? null : _resetPassword,
              style: ElevatedButton.styleFrom(
                backgroundColor: Color.fromARGB(255, 147, 182, 138),
                minimumSize: Size(double.infinity, 50),
              ),
              child: _loading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text(
                      "Change Password",
                      style: TextStyle(fontSize: 18, color: Colors.white),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
