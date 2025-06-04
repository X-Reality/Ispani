import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ispani/Controllers/DisplaySettingsProvider.dart';

class DisplaySettingsScreen extends StatelessWidget {
  const DisplaySettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final displayProvider = Provider.of<DisplaySettingsProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text("Display Settings")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Font Size", style: TextStyle(fontWeight: FontWeight.bold)),
            Slider(
              value: displayProvider.fontSize,
              min: 0.8,
              max: 1.5,
              divisions: 7,
              label: "${(displayProvider.fontSize * 100).round()}%",
              onChanged: (newSize) {
                displayProvider.setFontSize(newSize);
              },
            ),
            const SizedBox(height: 20),
            const Text("Preview:"),
            Text(
              "This is a sample preview text.",
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}
