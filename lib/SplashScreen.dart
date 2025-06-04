import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'dart:async';
import 'WelcomeScreen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool? _hasConnection;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  @override
  void initState() {
    super.initState();
    _startListening();
    _initialConnectionCheck();
  }

  Future<void> _initialConnectionCheck() async {
    var results = await Connectivity().checkConnectivity();
    final result = results.isNotEmpty ? results.first : ConnectivityResult.none;
    _updateConnectionStatus(result);
  }

  void _startListening() {
    _connectivitySubscription = Connectivity()
        .onConnectivityChanged
        .listen((List<ConnectivityResult> results) {
      final result =
      results.isNotEmpty ? results.first : ConnectivityResult.none;
      _updateConnectionStatus(result);
    });
  }

  void _updateConnectionStatus(ConnectivityResult result) {
    bool connected = result != ConnectivityResult.none;
    if (connected && _hasConnection != true) {
      setState(() {
        _hasConnection = true;
      });

      // Only navigate once
      Future.delayed(const Duration(seconds: 2), () {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const WelcomeScreen()),
        );
      });
    } else if (!connected) {
      setState(() {
        _hasConnection = false;
      });
    }
  }

  @override
  void dispose() {
    _connectivitySubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget content;

    if (_hasConnection == null) {
      content = Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Image.asset('assets/img.png', height: 200, width: 200),
          const SizedBox(height: 20),
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(
                Color.fromARGB(255, 147, 182, 138)),
          ),
        ],
      );
    } else if (_hasConnection == false) {
      content = Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.wifi_off, size: 80, color: Colors.red),
          SizedBox(height: 20),
          Text(
            'No internet connection.\nWaiting for connection...',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
        ],
      );
    } else {
      content = Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Image.asset('assets/img.png', height: 200, width: 200),
          const SizedBox(height: 20),
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(
                Color.fromARGB(255, 147, 182, 138)),
          ),
        ],
      );
    }

    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(child: content),
    );
  }
}
