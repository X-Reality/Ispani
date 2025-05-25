import 'package:flutter/material.dart';
import 'package:ispani/TutorHomeScreen.dart';
import 'TutoringProfileScreen.dart';
import 'package:ispani/GroupsScreen.dart';
import 'package:ispani/MessagesScreen.dart';
import 'package:ispani/ProfileScreen.dart';

class TutorsScreen extends StatefulWidget {
  const TutorsScreen({super.key});

  @override
  State<TutorsScreen> createState() => _TutorsScreenState();
}

class _TutorsScreenState extends State<TutorsScreen> {
  final List<String> categories = [
    "All", "Design", "Coding", "Mobile", "Web", "Flutter", "JavaScript", "React", "Dart"
  ];

  int selectedCategoryIndex = 0;
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    TutorHomeScreen(),
    MessagesScreen(),
    Container(), // Explore
    GroupsScreen(),
    ProfileScreen(),
  ];

  final List<Map<String, dynamic>> allTutors = [
    {
      'name': 'Khanyisile Jackson',
      'subject': 'Intro to Drone Tech',
      'tags': ['Design', 'HTML', 'CSS', 'React'],
      'students': 37,
      'reviews': 38,
      'hours': 200,
      'description': 'Expert in frontend web development.',
      'avatar': 'assets/backgroung.jpg'
    },
    {
      'name': 'Richard Nelson',
      'subject': 'Mobile App Development',
      'tags': ['Flutter', 'Dart', 'Mobile'],
      'students': 37,
      'reviews': 20,
      'hours': 200,
      'description': '',
      'avatar': 'assets/backgroung.jpg'
    },
    {
      'name': 'Linda Mokoena',
      'subject': 'JavaScript Essentials',
      'tags': ['JavaScript', 'Web', 'React'],
      'students': 22,
      'reviews': 15,
      'hours': 150,
      'description': 'Build interactive web apps.',
      'avatar': 'assets/backgroung.jpg'
    },
    {
      'name': 'Thabiso Lekota',
      'subject': 'UI/UX Design Principles',
      'tags': ['Design', 'UI/UX'],
      'students': 18,
      'reviews': 25,
      'hours': 120,
      'description': 'Learn user-first design.',
      'avatar': 'assets/backgroung.jpg'
    },
  ];

  void _onTabSelected(int index) {
    if (index == 2) {
      _showBottomDrawer();
    } else {
      setState(() {
        _selectedIndex = index;
      });
    }
  }

  void _showBottomDrawer() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return FractionallySizedBox(
          heightFactor: 0.5,
          child: Column(
            children: [
              Container(
                margin: const EdgeInsets.only(top: 10),
                width: 40,
                height: 5,
                decoration: BoxDecoration(
                  color: Colors.grey,
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                "Explore More",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              Expanded(
                child: ListView(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.trending_up),
                      title: const Text("Trending"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: const Icon(Icons.new_releases),
                      title: const Text("Latest"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: const Icon(Icons.category),
                      title: const Text("Categories"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: const Icon(Icons.people),
                      title: const Text("Communities"),
                      onTap: () {},
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final String selectedCategory = categories[selectedCategoryIndex];
    final List<Map<String, dynamic>> filteredTutors = selectedCategory == 'All'
        ? allTutors
        : allTutors.where((tutor) => tutor['tags'].contains(selectedCategory)).toList();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text('Tutors', style: TextStyle(color: Colors.black)),
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.more_vert, color: Colors.black)),
        ],
      ),
      body: Column(
        children: [
          const SizedBox(height: 10),
          _buildCategoryFilters(),
          const SizedBox(height: 10),
          Expanded(child: _buildTutorList(filteredTutors)),
        ],
      ),
      bottomNavigationBar: CustomBottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onTabSelected,
      ),
    );
  }

  Widget _buildCategoryFilters() {
    return SizedBox(
      height: 60,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 16),
        itemBuilder: (context, index) {
          final isSelected = selectedCategoryIndex == index;
          return ChoiceChip(
            label: Text(categories[index]),
            selected: isSelected,
            selectedColor: Colors.green[200],
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 16),
            backgroundColor: Colors.grey[200],
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(26)),
            onSelected: (_) {
              setState(() {
                selectedCategoryIndex = index;
              });
            },
          );
        },
      ),
    );
  }

  Widget _buildTutorList(List<Map<String, dynamic>> tutors) {
    return ListView.builder(
      itemCount: tutors.length,
      itemBuilder: (context, index) {
        final tutor = tutors[index];
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: _tutorCard(context, tutor),
        );
      },
    );
  }

  Widget _tutorCard(BuildContext context, Map<String, dynamic> tutor) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey, width: 1),
        color: Colors.white,
      ),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        color: Colors.white,
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(backgroundImage: AssetImage(tutor['avatar']), radius: 24),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          tutor['name'],
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 22),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.school, size: 16),
                            Text(" ${tutor['students']}  "),
                            const SizedBox(width: 10),
                            const Icon(Icons.timer, size: 16),
                            Text(" ${tutor['hours']}  "),
                            const SizedBox(width: 10),
                            const Icon(Icons.star, size: 16),
                            Text(" ${tutor['reviews']}"),
                          ],
                        ),
                      ],
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.grey[300],
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.favorite, color: Colors.black),
                      onPressed: () {},
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  tutor['subject'],
                  style: const TextStyle(
                    fontWeight: FontWeight.w900,
                    fontSize: 30,
                    color: Colors.green,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 22,
                children: List.generate(
                  tutor['tags'].length,
                      (index) => Chip(
                    label: Text(
                      '#${tutor['tags'][index]}',
                      style: const TextStyle(fontSize: 10),
                    ),
                    backgroundColor: Colors.grey[200],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              if (tutor['description'] != '')
                Text(tutor['description'], style: const TextStyle(fontSize: 15)),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color.fromARGB(255, 147, 182, 138),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        minimumSize: const Size(double.infinity, 45),
                      ),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => TutorProfileScreen(tutor: Tutor(name: "name", subject: "", bio: "bio"),),
                          ),
                        );
                      },
                      child: const Text(
                        "Book a Lesson",
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.rectangle,
                      color: Colors.grey[300],
                      borderRadius: const BorderRadius.all(Radius.circular(10)),
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.message_outlined, color: Colors.black),
                      onPressed: () {},
                    ),
                  ),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}

class CustomBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const CustomBottomNavigationBar({
    required this.currentIndex,
    required this.onTap,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      type: BottomNavigationBarType.fixed,
      currentIndex: currentIndex,
      onTap: onTap,
      selectedItemColor: const Color.fromARGB(255, 147, 182, 138),
      unselectedItemColor: Colors.grey,
      backgroundColor: Colors.white,
      items: [
        const BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
        const BottomNavigationBarItem(icon: Icon(Icons.message), label: "Messages"),
        BottomNavigationBarItem(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: const BoxDecoration(
              color: Color.fromARGB(255, 147, 182, 138),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.explore, color: Colors.white),
          ),
          label: "",
        ),
        const BottomNavigationBarItem(icon: Icon(Icons.supervised_user_circle), label: "Groups"),
        const BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
      ],
    );
  }
}
