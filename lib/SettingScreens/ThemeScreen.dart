import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ispani/Controllers/Theme_provider.dart';
import 'package:ispani/utils.dart';

class ThemeScreen extends StatelessWidget {
  const ThemeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Theme Selection", style: TextStyle(color: Colors.black)),

        iconTheme: const IconThemeData(color: Colors.white),
        elevation: 0.5,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          SwitchListTile(
            title: const Text("Dark Mode"),
            subtitle: const Text("Enable dark theme across the app"),
            value: themeProvider.isDarkMode,
            onChanged: themeProvider.toggleTheme,
            secondary: const Icon(Icons.brightness_6),
          ),
        ],
      ),
    );
  }
}
