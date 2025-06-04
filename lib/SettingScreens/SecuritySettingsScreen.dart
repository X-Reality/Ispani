import 'package:flutter/material.dart';
import 'package:ispani/Services/SecuritySettingsStorage.dart';
import 'package:ispani/Services/biometricService.dart';
import 'package:ispani/SettingScreens/LockTypeSettingsScreen.dart';
import 'package:ispani/SettingScreens/PinScreen.dart';

class SecuritySettingsScreen extends StatefulWidget {
  const SecuritySettingsScreen({super.key});

  @override
  State<SecuritySettingsScreen> createState() => _SecuritySettingsScreenState();
}

class _SecuritySettingsScreenState extends State<SecuritySettingsScreen> {
  bool _biometricsEnabled = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final isEnabled = await SecuritySettingsStorage.isBiometricEnabled();
    setState(() => _biometricsEnabled = isEnabled);
  }

  Future<void> _toggleBiometrics(bool value) async {
    final canUse = await BiometricService.canCheckBiometrics();
    if (!canUse) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Biometrics not available.")),
      );
      return;
    }
    await SecuritySettingsStorage.setBiometricEnabled(value);
    setState(() => _biometricsEnabled = value);
  }




  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Security Settings')),
      body: ListView(
        children: [
          const ListTile(
            title: Text("PIN Code"),
            subtitle: Text("Used for locking/unlocking the app."),
          ),
          ListTile(
            title: const Text("Set/Change PIN"),
            trailing: const Icon(Icons.chevron_right),
              onTap: (){
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const SetPinScreen()),
                );
              }
          ),
          SwitchListTile(
            title: const Text("Enable Biometrics"),
            value: _biometricsEnabled,
            onChanged: _toggleBiometrics,
          ),
          ListTile(
            title: const Text("Lock Type"),
            subtitle: const Text("Choose how the app locks (e.g. on launch, after timeout)"),
            trailing: const Icon(Icons.chevron_right),
            onTap: (){
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const LockTypeSettingsScreen()),
              );
            }

          ),
        ],
      ),
    );
  }
}
