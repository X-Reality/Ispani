import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PolicySettingsScreen extends StatefulWidget {
  const PolicySettingsScreen({super.key});

  @override
  State<PolicySettingsScreen> createState() => _PolicySettingsScreenState();
}

class _PolicySettingsScreenState extends State<PolicySettingsScreen> {
  bool _acceptedPolicies = false;

  @override
  void initState() {
    super.initState();
    _loadConsentStatus();
  }

  Future<void> _loadConsentStatus() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _acceptedPolicies = prefs.getBool('acceptedPolicies') ?? false;
    });
  }

  Future<void> _updateConsentStatus(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('acceptedPolicies', value);
    setState(() {
      _acceptedPolicies = value;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(value ? "Policy accepted" : "Policy acceptance removed"),
      ),
    );
  }

  Future<void> _launchPolicyUrl(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Could not open policy URL")),
      );
    }
  }

  void _sendDeleteRequest() async {
    final uri = Uri(
      scheme: 'mailto',
      path: 'support@yourapp.com',
      query: 'subject=Delete My Data&body=Please delete all my personal data associated with this account.',
    );
    if (!await launchUrl(uri)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Could not open email client")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Policy Settings")),
      body: ListView(
        children: [
          ListTile(
            title: const Text("Privacy Policy"),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _launchPolicyUrl("https://your-site.com/privacy-policy"),
          ),
          ListTile(
            title: const Text("Terms and Conditions"),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _launchPolicyUrl("https://your-site.com/terms-and-conditions"),
          ),
          ListTile(
            title: const Text("Data Usage Policy"),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _launchPolicyUrl("https://your-site.com/data-usage"),
          ),
          const Divider(),
          SwitchListTile(
            title: const Text("I accept the app policies"),
            value: _acceptedPolicies,
            onChanged: _updateConsentStatus,
          ),
          const Divider(),
          ListTile(
            title: const Text("Delete My Data"),
            subtitle: const Text("Send a request to remove all your data"),
            trailing: const Icon(Icons.delete_forever, color: Colors.red),
            onTap: _sendDeleteRequest,
          ),
        ],
      ),
    );
  }
}
