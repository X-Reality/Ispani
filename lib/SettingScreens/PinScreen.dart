import 'package:flutter/material.dart';
import 'package:ispani/Services/PinService.dart';

class SetPinScreen extends StatefulWidget {
  const SetPinScreen({super.key});

  @override
  State<SetPinScreen> createState() => _SetPinScreenState();
}

class _SetPinScreenState extends State<SetPinScreen> {
  final _pinController = TextEditingController();

  void _savePin() async {
    final pin = _pinController.text.trim();
    if (pin.length == 4) {
      await PinService.setPin(pin);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("PIN set successfully")),
      );
      Navigator.pop(context); // Go back to settings or lock screen
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("PIN must be 4 digits")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Set PIN")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text("Enter a 4-digit PIN"),
            TextField(
              controller: _pinController,
              keyboardType: TextInputType.number,
              maxLength: 4,
              obscureText: true,
              decoration: const InputDecoration(labelText: "PIN"),
            ),
            ElevatedButton(onPressed: _savePin, child: const Text("Save PIN"))
          ],
        ),
      ),
    );
  }
}
