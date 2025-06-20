import 'dart:convert';
import 'package:http/http.dart' as http;

class PaystackService {
  static const String _baseUrl = 'https://api.paystack.co';

  final String secretKey;

  PaystackService(this.secretKey);

  Future<String> initializeTransaction({
    required String email,
    required int amount,
    required String reference,
    Map<String, String>? metadata,
  }) async {
    final url = Uri.parse('$_baseUrl/transaction/initialize');
    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $secretKey',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'email': email,
        'amount': amount.toString(),
        'reference': reference,
        'metadata': metadata,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['data']['authorization_url'];
    } else {
      throw Exception('Failed to initialize transaction: ${response.body}');
    }
  }

  Future<bool> verifyTransaction(String reference) async {
    final url = Uri.parse('$_baseUrl/transaction/verify/$reference');
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $secretKey',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['data']['status'] == 'success';
    }
    return false;
  }
}