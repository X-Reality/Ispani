import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class ContactSupportScreen extends StatefulWidget {
  const ContactSupportScreen({Key? key}) : super(key: key);

  @override
  State<ContactSupportScreen> createState() => _ContactSupportScreenState();
}

class _ContactSupportScreenState extends State<ContactSupportScreen> {
  final _formKey = GlobalKey<FormState>();



  final String whatsappNumber = '+27715289453'; // Full number with country code

  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _messageController = TextEditingController();

  Future<void> _makePhoneCall() async {
    final Uri uri = Uri(scheme: 'tel', path: '+27715289453');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      _showError("Could not open phone app.");
    }
  }


  void _sendDeleteRequest() async {
    final uri = Uri(
      scheme: 'mailto',
      path: 'support@yourapp.com',
      query: 'subject=Delete My Data&body=Please delete all my personal data associated with this account.',
    );
    if (!await launchUrl(uri)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Could not open email client")),
      );
    }
  }

  Future<void> _openWhatsApp() async {
    final Uri whatsappUri = Uri.parse("https://wa.me/${whatsappNumber.replaceAll('+', '')}?text=Hello%20support");
    if (await canLaunchUrl(whatsappUri)) {
      await launchUrl(whatsappUri);
    } else {
      _showError("Could not open WhatsApp.");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      // Here you could also send this to an API or email service.
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Message sent successfully')),
      );
      _nameController.clear();
      _emailController.clear();
      _messageController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Contact Support")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Get in touch with our support team.", style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 20),

            // Call Support

            // Email Support
            ListTile(
              leading: const Icon(Icons.email, color: Colors.blue),
              title: const Text("Email Us"),
              subtitle: Text('Support@example.com'),
              trailing: ElevatedButton.icon(
                onPressed: _sendDeleteRequest,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color.fromARGB(255, 147, 182, 138),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                icon: const Icon(Icons.mail,color: Colors.white,),
                label: const Text("Email",style: TextStyle(color: Colors.white),),
              ),
            ),

            // WhatsApp Support
            ListTile(
              leading: const Icon(Icons.chat, color: Colors.teal),
              title: const Text("Chat on WhatsApp"),
              subtitle: Text(whatsappNumber),
              trailing: ElevatedButton.icon(
                onPressed: _openWhatsApp,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color.fromARGB(255, 147, 182, 138),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                icon: const Icon(Icons.chat_bubble_outline,color: Colors.white,),
                label: const Text("Chat",style: TextStyle(color: Colors.white),),
              ),
            ),

            const SizedBox(height: 30),
            const Divider(),
            const SizedBox(height: 30),
            Text("Or send us a message:", style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 30),

            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _nameController,
                    decoration: InputDecoration(
                      labelText: "Name",
                      hintText: "Enter your Name",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    validator: (value) => value!.isEmpty ? 'Enter your name' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _emailController,
                    decoration: InputDecoration(
                      labelText: "Email",
                      hintText: "Enter your Email",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) return 'Enter your email';
                      if (!value.contains('@')) return 'Enter a valid email';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      labelText: "Messages",
                      hintText: "Enter your Messages",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    maxLines: 4,
                    validator: (value) => value!.isEmpty ? 'Enter your message' : null,
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _submitForm,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color.fromARGB(255, 147, 182, 138), // Change background color
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12), // Change border radius
                        ),
                        minimumSize: Size(double.infinity, 50), // Make it full width
                      ),
                      icon: const Icon(Icons.send,color: Colors.white,),
                      label: const Text("Send Message",style: TextStyle(color: Colors.white),),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
