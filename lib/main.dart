import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ispani/Controllers/Theme_provider.dart';
import 'package:ispani/Controllers/DisplaySettingsProvider.dart';
import 'SplashScreen.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => DisplaySettingsProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final displaySettings = Provider.of<DisplaySettingsProvider>(context);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'My Flutter App',
      themeMode: themeProvider.currentTheme,
      theme: ThemeData.light(),
      darkTheme: ThemeData.dark(),
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(textScaleFactor: displaySettings.fontSize),
          child: child!,
        );
      },
      home: const SplashScreen(),
    );
  }
}
