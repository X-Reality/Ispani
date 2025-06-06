import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'HomeScreen.dart';
import 'Login.dart';
import 'TutorHomeScreen.dart';
import 'package:ispani/Controllers/Theme_provider.dart';
import 'package:ispani/Controllers/DisplaySettingsProvider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  SharedPreferences prefs = await SharedPreferences.getInstance();
  bool isLoggedIn = prefs.getBool('isLoggedIn') ?? false;
  String userRole = prefs.getString('userRole') ?? '';

  Widget startScreen;
  if (isLoggedIn) {
    startScreen = (userRole == 'tutor') ? TutorHomeScreen() : HomeScreen();
  } else {
    startScreen = LoginScreen();
  }

  runApp(MyApp(startScreen: startScreen));
}

class MyApp extends StatelessWidget {
  final Widget startScreen;
  const MyApp({super.key, required this.startScreen});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => DisplaySettingsProvider()),
      ],
      child: Consumer2<ThemeProvider, DisplaySettingsProvider>(
        builder: (context, themeProvider, displaySettings, child) {
          return MaterialApp(
            debugShowCheckedModeBanner: false,
            title: 'Ispani App',
            themeMode: themeProvider.currentTheme,
            theme: ThemeData.light(),
            darkTheme: ThemeData.dark(),
            builder: (context, child) {
              return MediaQuery(
                data: MediaQuery.of(context).copyWith(
                  textScaleFactor: displaySettings.fontSize,
                ),
                child: child!,
              );
            },
            home: startScreen,
          );
        },
      ),
    );
  }
}
