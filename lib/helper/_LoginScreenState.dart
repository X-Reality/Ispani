import 'package:local_auth/local_auth.dart';

final LocalAuthentication auth = LocalAuthentication();

Future<bool> _authenticateWithBiometrics() async {
  try {
    final bool canAuthenticate = await auth.canCheckBiometrics || await auth.isDeviceSupported();

    if (!canAuthenticate) return false;

    return await auth.authenticate(
      localizedReason: 'Please authenticate to login',
      options: const AuthenticationOptions(
        biometricOnly: true,
        stickyAuth: true,
      ),
    );
  } catch (e) {
    print("Biometric auth error: $e");
    return false;
  }
}
