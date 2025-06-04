import 'package:flutter/material.dart';

class LockTypeSettingsScreen extends StatefulWidget {
  const LockTypeSettingsScreen({Key? key}) : super(key: key);

  @override
  State<LockTypeSettingsScreen> createState() => _LockTypeSettingsScreenState();
}

class _LockTypeSettingsScreenState extends State<LockTypeSettingsScreen> {
  String? _selectedLockType;

  final List<String> lockTypes = [
    'None',
    'PIN',
    'Password',
    'Biometric (Fingerprint/Face ID)',
  ];

  @override
  void initState() {
    super.initState();
    // TODO: Load saved lock type from persistent storage if needed
    _selectedLockType = 'None'; // Default value
  }

  void _onLockTypeChanged(String? newValue) {
    setState(() {
      _selectedLockType = newValue;
      // TODO: Save the choice persistently here (SharedPreferences or similar)
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Lock Type'),
      ),
      body: ListView.builder(
        itemCount: lockTypes.length,
        itemBuilder: (context, index) {
          final type = lockTypes[index];
          return RadioListTile<String>(
            title: Text(type),
            value: type,
            groupValue: _selectedLockType,
            onChanged: _onLockTypeChanged,
          );
        },
      ),
    );
  }
}
