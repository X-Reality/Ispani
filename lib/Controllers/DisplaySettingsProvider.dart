import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class DisplaySettingsProvider extends ChangeNotifier {
  double _fontSize = 1.0; // Default text scale factor (1.0 = normal)

  double get fontSize => _fontSize;

  DisplaySettingsProvider() {
    _loadSettings();
  }

  void setFontSize(double newSize) async {
    _fontSize = newSize;
    notifyListeners();

    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('fontSize', _fontSize);
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _fontSize = prefs.getDouble('fontSize') ?? 1.0;
    notifyListeners();
  }
}
