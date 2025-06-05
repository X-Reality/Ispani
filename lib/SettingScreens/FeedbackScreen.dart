import 'package:flutter/material.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({Key? key}) : super(key: key);

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _feedbackController = TextEditingController();

  void _submitFeedback() {
    if (_formKey.currentState!.validate()) {
      // Simulate sending feedback
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Feedback submitted successfully!')),
      );
      _nameController.clear();
      _emailController.clear();
      _feedbackController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Feedback')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "We'd love your feedback!",
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 20),

              /// Name
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Your Name'),
                validator: (value) =>
                value == null || value.isEmpty ? 'Enter your name' : null,
              ),
              const SizedBox(height: 12),

              /// Email
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Your Email'),
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Enter your email';
                  if (!value.contains('@')) return 'Enter a valid email';
                  return null;
                },
              ),
              const SizedBox(height: 12),

              /// Feedback
              TextFormField(
                controller: _feedbackController,
                decoration: const InputDecoration(labelText: 'Your Feedback'),
                maxLines: 5,
                validator: (value) => value == null || value.isEmpty
                    ? 'Please enter your feedback'
                    : null,
              ),
              const SizedBox(height: 20),

              /// Submit Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _submitFeedback,
                  icon: const Icon(Icons.send),
                  label: const Text("Submit Feedback"),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
