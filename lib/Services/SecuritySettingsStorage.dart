import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecuritySettingsStorage {
  static final _storage = FlutterSecureStorage();
  static const _biometricKey = 'use_biometrics';

  static Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.write(key: _biometricKey, value: enabled.toString());
  }

  static Future<bool> isBiometricEnabled() async {
    final value = await _storage.read(key: _biometricKey);
    return value == 'true';
  }
}
