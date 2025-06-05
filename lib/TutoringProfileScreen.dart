import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:ispani/TutorBookingScreen.dart';

class Tutor {
  final String name;
  final String subject;
  final String bio;

  Tutor({
    required this.name,
    required this.subject,
    required this.bio,
  });
}

class TutorProfileScreen extends StatelessWidget {
  final Tutor tutor; // Accept Tutor data via constructor

  TutorProfileScreen({required this.tutor});

  void _showIntroVideo(BuildContext context) {
    final videoId = YoutubePlayer.convertUrlToId("https://www.youtube.com/watch?v=dQw4w9WgXcQ");

    YoutubePlayerController _controller = YoutubePlayerController(
      initialVideoId: videoId!,
      flags: YoutubePlayerFlags(
        autoPlay: true,
        mute: false,
      ),
    );

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        contentPadding: EdgeInsets.zero,
        content: AspectRatio(
          aspectRatio: 16 / 9,
          child: YoutubePlayer(
            controller: _controller,
            showVideoProgressIndicator: true,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(

      appBar: AppBar(

        title: Text("Tutor Profile"),
      ),
      body: Column(
        children: [
          // Banner with play icon and centered avatar
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: double.infinity,
                height: 180,
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage("assets/images (1).jpeg"),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              Positioned(
                top: 16,
                right: 16,
                child: InkWell(
                  onTap: () => _showIntroVideo(context),
                  child: CircleAvatar(
                    backgroundColor: Colors.black54,
                    radius: 26,
                    child: Icon(Icons.play_arrow, color: Colors.white, size: 30),
                  ),
                ),
              ),
              Positioned(
                bottom: -50,
                left: 0,
                right: 0,
                child: Center(
                  child: CircleAvatar(
                    radius: 50,
                    backgroundImage: AssetImage("assets/images (2).jpeg"),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 60), // for avatar space

          // Name and title
          Text(
            tutor.name,
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 4),
          Text("${tutor.subject} | 5+ Years Experience"),

          SizedBox(height: 16),

          // Intro Paragraph
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              tutor.bio,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.black87),
            ),
          ),

          SizedBox(height: 20),

          // Stats
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: GridView.count(
              shrinkWrap: true,
              crossAxisCount: 4,
              physics: NeverScrollableScrollPhysics(),
              crossAxisSpacing: 12,
              mainAxisSpacing: 30,
              children: [
                _statBox("Students", "200"),
                _statBox("Hours", "384"),
                _statBox("Lessons", "34"),
                _statBox("Reviews", "38"),
              ],
            ),
          ),

          Spacer(),

          // Book Button
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => TutorBookingForm(tutorName: tutor.name),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green[200],
                padding: EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                minimumSize: Size(double.infinity, 50),
              ),
              child: Text("Book a Lesson", style: TextStyle(fontSize: 18, color: Colors.white)),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        selectedItemColor: Colors.green,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
          BottomNavigationBarItem(icon: Icon(Icons.school), label: "Tutoring"),
          BottomNavigationBarItem(icon: Icon(Icons.message), label: "Message"),
          BottomNavigationBarItem(icon: Icon(Icons.group), label: "Groups"),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
        ],
      ),
    );
  }

  Widget _statBox(String title, String value) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Text(title, style: TextStyle(color: Colors.grey)),
      ],
    );
  }
}
