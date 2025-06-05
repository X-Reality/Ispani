import 'package:flutter/material.dart';

class DeregistrationScreen extends StatefulWidget {
  @override
  _DeregistrationScreenState createState() => _DeregistrationScreenState();
}

class _DeregistrationScreenState extends State<DeregistrationScreen> {
  final TextEditingController _reasonController = TextEditingController();
  bool _confirmDelete = false;

// Replace with exact green if different


  void _handleDeregistration() {
    if (_confirmDelete) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Account deregistered successfully.")),
      );
      // Navigate or handle deletion logic
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Please confirm you want to delete your account.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(

      appBar: AppBar(

        title: Text("Deregister Account"),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "We're sorry to see you go.",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, ),
            ),
            SizedBox(height: 20),
            Text(
              "By deleting your account, you acknowledge and agree to the following terms:\n\n"
                  "• Your account and all associated data will be permanently removed from our system.\n"
                  "• This action cannot be undone. You will lose access to all your information, history, and services.\n"
                  "• Any active subscriptions or pending transactions will be canceled immediately.\n"
                  "• We may retain minimal data for legal or regulatory purposes in accordance with our privacy policy.\n"
                  "• If you signed in using a business account, ensure you've handled all business-related responsibilities before proceeding.\n\n"
                  "For more details, please review our Privacy Policy and Terms of Service.",
              style: TextStyle(fontSize: 14, ),
            ),

            SizedBox(height: 20),
            TextField(
              controller: _reasonController,
              maxLines: 4,
              decoration: InputDecoration(
                labelText: "Reason for leaving (optional)",
                filled: true,

                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20),
            // 👇 Vector illustration goes here

            Container(
              decoration: BoxDecoration(

                borderRadius: BorderRadius.circular(8),
              ),
              child: CheckboxListTile(
                title: Text("I understand this action is permanent."),
                value: _confirmDelete,

                onChanged: (value) {
                  setState(() {
                    _confirmDelete = value!;
                  });
                },
              ),
            ),
            SizedBox(height: 30),
            Center(
              child: ElevatedButton.icon(
                onPressed: _handleDeregistration,
                icon: Icon(Icons.delete_forever,color: Colors.white,),
                label: Text("Deregister My Account"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  textStyle: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
