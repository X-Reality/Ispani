import 'package:flutter/material.dart';

class HelpFaqScreen extends StatefulWidget {
  const HelpFaqScreen({Key? key}) : super(key: key);

  @override
  State<HelpFaqScreen> createState() => _HelpFaqScreenState();
}

class _HelpFaqScreenState extends State<HelpFaqScreen> {
  final TextEditingController _searchController = TextEditingController();

  // Sample FAQ list
  List<Map<String, String>> faqs = [
    {
      'question': 'How do I reset my password?',
      'answer': 'Go to the login screen, tap "Forgot password", and follow the instructions.'
    },
    {
      'question': 'How do I enable biometric login?',
      'answer': 'Go to Settings > Security and enable biometric authentication.'
    },
    {
      'question': 'How can I contact support?',
      'answer': 'Scroll down and tap on "Contact Support".'
    },
    {
      'question': 'Where can I view my bookings?',
      'answer': 'You can view all bookings from the Home screen or Booking tab.'
    },
  ];

  String searchQuery = '';

  @override
  Widget build(BuildContext context) {
    List<Map<String, String>> filteredFaqs = faqs
        .where((faq) =>
        faq['question']!.toLowerCase().contains(searchQuery.toLowerCase()))
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: Text('Help & FAQs'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Search Field
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                labelText: 'Search FAQs',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onChanged: (query) {
                setState(() {
                  searchQuery = query;
                });
              },
            ),
            const SizedBox(height: 20),

            // FAQs
            Expanded(
              child: filteredFaqs.isEmpty
                  ? Center(child: Text('No FAQs found.'))
                  : ListView.builder(
                itemCount: filteredFaqs.length,
                itemBuilder: (context, index) {
                  final faq = filteredFaqs[index];
                  return ExpansionTile(
                    title: Text(faq['question']!),
                    children: [
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16.0, vertical: 8.0),
                        child: Text(faq['answer']!),
                      )
                    ],
                  );
                },
              ),
            ),

            // Contact Support
            const Divider(),
            ListTile(
              leading: Icon(Icons.support_agent),
              title: Text('Need more help?'),
              subtitle: Text('Contact our support team.'),
              trailing: Icon(Icons.chevron_right),
              onTap: () {
                // Navigate or open support dialog
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: Text('Contact Support'),
                    content: Text('Email us at support@yourapp.com or call +123456789.'),
                    actions: [
                      TextButton(
                        child: Text('Close'),
                        onPressed: () => Navigator.of(context).pop(),
                      )
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
