import 'package:flutter/material.dart';
import 'package:ispani/BookingCalendarScreen.dart';
import 'package:ispani/GroupsScreen.dart';
import 'package:ispani/MessagesScreen.dart';
import 'package:ispani/ProfileScreen.dart';
import 'package:ispani/SettingScreen.dart';
import 'package:ispani/TutoringScreen.dart';
import 'package:ispani/De-registration.dart';

void main() {
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    home: HomeScreen(),
  ));
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  // Screens for each tab
  final List<Widget> _screens = [
    HomeTabScreen(),
    MessagesScreen(),
    Container(), // Placeholder for Explore, handled separately
    GroupsScreen(),
    ProfileScreen(),
  ];

  void _onTabSelected(int index) {
    if (index == 2) {
      _showBottomDrawer(); // Open Explore drawer
    } else {
      setState(() {
        _selectedIndex = index;
      });
    }
  }

  // Bottom Drawer for Explore Tab
  void _showBottomDrawer() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return FractionallySizedBox(
          heightFactor: 0.5, // 50% screen height
          child: Column(
            children: [
              Container(
                margin: EdgeInsets.only(top: 10),
                width: 40,
                height: 5,
                decoration: BoxDecoration(
                  color: Colors.grey,
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              SizedBox(height: 10),
              Text(
                "Explore More",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              Expanded(
                child: ListView(
                  children: [
                    ListTile(
                      leading: Icon(Icons.trending_up),
                      title: Text("Trending"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: Icon(Icons.new_releases),
                      title: Text("Latest"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: Icon(Icons.category),
                      title: Text("Categories"),
                      onTap: () {},
                    ),
                    ListTile(
                      leading: Icon(Icons.people),
                      title: Text("Communities"),
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
    return Scaffold(

      body: _selectedIndex == 2 ? Container() : _screens[_selectedIndex],
      bottomNavigationBar: CustomBottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onTabSelected,
      ),
    );
  }
}

// Custom Bottom Navigation Bar
class CustomBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  CustomBottomNavigationBar({required this.currentIndex, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      type: BottomNavigationBarType.fixed,
      currentIndex: currentIndex,
      onTap: onTap,
      selectedItemColor: Color.fromARGB(255, 147, 182, 138),
      unselectedItemColor: Colors.grey,

      items: [
        BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
        BottomNavigationBarItem(icon: Icon(Icons.message), label: "Messages"),
        BottomNavigationBarItem(icon: Icon(Icons.timer_outlined), label: "Updates"),
        BottomNavigationBarItem(icon: Icon(Icons.supervised_user_circle), label: "Groups"),
        BottomNavigationBarItem(icon: Icon(Icons.account_circle_outlined), label: "Profile"),
      ],
    );
  }
}

// Home Tab Screen
class HomeTabScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(

      appBar: AppBar(

        elevation: 0,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "Search",
                  filled: true,

                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: Icon(Icons.search, color: Colors.grey),
                ),
              ),
            ),
            SizedBox(width: 10),
            Padding(
              padding: const EdgeInsets.only(right: 12.0),
              child: PopupMenuButton<String>(
                offset: Offset(0, 50), // 👈 pushes menu downward under profile pic
                color: Colors.white,
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                onSelected: (value) {
                  switch (value) {
                    case 'business':
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => DeregistrationScreen()),
                      );
                      break;
                    case 'settings':
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => SettingsScreen()),
                      );
                      break;
                    case 'logout':
                    // Handle logout
                      break;
                  }
                },
                icon: CircleAvatar(
                  backgroundImage: AssetImage('assets/images (1).jpeg'),
                  radius: 18,
                ),
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'business',
                    child: Row(
                      children: [
                        Icon(Icons.business, color: Color(0xFF2E7D32)),
                        SizedBox(width: 10),
                        Text("Sign in as Business"),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'settings',
                    child: Row(
                      children: [
                        Icon(Icons.settings, color: Color(0xFF2E7D32)),
                        SizedBox(width: 10),
                        Text("Settings"),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'logout',
                    child: Row(
                      children: [
                        Icon(Icons.logout, color: Color(0xFF2E7D32)),
                        SizedBox(width: 10),
                        Text("Logout"),
                      ],
                    ),
                  ),
                ],
              ),
            ),


          ]
    ),
    ),
      body: SingleChildScrollView(
        padding: EdgeInsets.symmetric(horizontal: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Communities", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                TextButton(
                  onPressed: () {},
                  child: Text("View all", style: TextStyle(color: Color.fromARGB(255, 147, 182, 138))),
                ),
              ],
            ),
            SizedBox(height: 10),
            Column(
              children: List.generate(1, (index) => _buildCommunityItems()),
            ),
            SizedBox(height: 20),
            Text("Explore", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 10),
            _buildServiceItems(context),
          ],
        ),
      ),
    );
  }
  Widget _buildCommunityItems() {
    final communities = [
      {
        "name": "weCode",
        "members": "23K",
        "description": "Where Code Comes Alive",
        "image": "assets/wecode.jpg"
      },
      {
        "name": "Flutter Devs",
        "members": "18K",
        "description": "Building Apps with Flutter",
        "image": "assets/flutter.jpg"
      },
      {
        "name": "AI Enthusiasts",
        "members": "15K",
        "description": "Exploring the Future of AI",
        "image": "assets/ai.jpg"
      },
      {
        "name": "UI/UX Creators",
        "members": "12K",
        "description": "Designing User Experiences",
        "image": "assets/uiux.jpg"
      },
    ];

    return Column(
      children: communities.take(4).map((community) {
        return ListTile(
          leading: CircleAvatar(
            backgroundImage: AssetImage(community["image"]!),
          ),
          title: Text(
            community["name"]!,
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text("${community["members"]} members - ${community["description"]}"),
          trailing: ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: Color.fromARGB(255, 147, 182, 138),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: Text("Join", style: TextStyle(color: Colors.white)),
          ),
        );
      }).toList(),
    );
  }



  Widget _buildServiceItems(BuildContext context) {
    final services = [
      "Book a Tutor",
    ];

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: services.map((service) {
        return SizedBox(
          width: 580,
          height: 80,
          child: GestureDetector(
            onTap: () {
              if (service == "Book a Tutor") {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => TutorsScreen()),
                );
              }
              else if(service == "calendar"){
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => BookingCalendarScreen(),
                  ),
                );
              }
            },
            child: Card(

              child: Center(child:Padding(padding: EdgeInsets.all(10), child:Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [

                      Icon(Icons.book_outlined),
                      SizedBox(width: 5,),
                      Text(service),
                    ],
                  ),
                  Icon(Icons.chevron_right),



                ],) ,)
                ,),
            ),
          ),
        );
      }).toList(),
    );
  }
}
