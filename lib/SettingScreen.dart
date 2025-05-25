import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black),
        elevation: 0.5,
      ),
      backgroundColor: Colors.grey[100],
      body: ListView(
        children: [
          _buildSectionTitle("Account"),
          _buildListTile(
            icon: Icons.person,
            title: "Edit Profile",
            description: "Update your name, photo, and personal details",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.lock,
            title: "Change Password",
            description: "Set a new secure password for your account",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.payment,
            title: "Payment Methods",
            description: "Manage your cards and payment preferences",
            onTap: () {},
          ),

          _buildSectionTitle("Preferences"),
          _buildListTile(
            icon: Icons.language,
            title: "Language",
            subtitle: "English",
            description: "Choose your preferred app language",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.brightness_6,
            title: "Theme",
            subtitle: "Light",
            description: "Switch between light and dark modes",
            onTap: () {},
          ),

          _buildSectionTitle("Notifications"),
          _buildSwitchTile(
            icon: Icons.notifications,
            title: "Push Notifications",
            description: "Get notified about upcoming sessions and updates",
            value: true,
            onChanged: (val) {},
          ),
          _buildSwitchTile(
            icon: Icons.email,
            title: "Email Alerts",
            description: "Receive important info in your email",
            value: false,
            onChanged: (val) {},
          ),

          _buildSectionTitle("Privacy & Security"),
          _buildListTile(
            icon: Icons.shield,
            title: "Privacy Policy",
            description: "Read how we protect your data",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.security,
            title: "Security Settings",
            description: "Control your login and verification settings",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.delete_forever,
            title: "Delete Account",
            description: "Permanently remove your account and data",
            onTap: () {},
          ),

          _buildSectionTitle("Support"),
          _buildListTile(
            icon: Icons.help_outline,
            title: "Help & FAQs",
            description: "Find answers to common questions",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.feedback_outlined,
            title: "Send Feedback",
            description: "Tell us how we can improve the app",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.support_agent,
            title: "Contact Support",
            description: "Reach out for technical or account help",
            onTap: () {},
          ),

          _buildSectionTitle("About"),
          _buildListTile(
            icon: Icons.info_outline,
            title: "About the App",
            subtitle: "Version 1.0.0",
            description: "Learn about this tutoring platform",
            onTap: () {},
          ),
          _buildListTile(
            icon: Icons.logout,
            title: "Log Out",
            description: "Sign out of your account",
            onTap: () {},
          ),
          const SizedBox(height: 30),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title.toUpperCase(),
        style: const TextStyle(
          fontSize: 14,
          color: Colors.grey,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildListTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required String description,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Icon(icon, color: Colors.green[700]),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (subtitle != null) Text(subtitle, style: const TextStyle(fontSize: 13)),
          Text(description, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    required String description,
    required bool value,
    required Function(bool) onChanged,
  }) {
    return SwitchListTile(
      secondary: Icon(icon, color: Colors.green[700]),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(description, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      value: value,
      onChanged: onChanged,
    );
  }
}
