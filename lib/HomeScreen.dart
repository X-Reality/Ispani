import 'package:flutter/material.dart';
import 'package:flutter_speed_dial/flutter_speed_dial.dart';
import 'package:ispani/GroupsScreen.dart';
import 'package:ispani/MessagesScreen.dart';
import 'package:ispani/ProfileScreen.dart';
import 'package:ispani/TutoringScreen.dart';

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
      backgroundColor: Colors.grey[100],
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
      selectedItemColor: Colors.blue,
      unselectedItemColor: Colors.grey,
      items: [
        BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
        BottomNavigationBarItem(icon: Icon(Icons.message), label: "Messages"),
        BottomNavigationBarItem(
          icon: Container(
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue,
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.explore, color: Colors.white),
          ),
          label: "",
        ),
        BottomNavigationBarItem(icon: Icon(Icons.supervised_user_circle), label: "Groups"),
        BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
      ],
    );
  }
}

// Home Tab Screen
class HomeTabScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "Search",
                  filled: true,
                  fillColor: Colors.grey[200],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: Icon(Icons.search, color: Colors.grey),
                ),
              ),
            ),
            SizedBox(width: 10),
            CircleAvatar(
              backgroundImage: AssetImage("assets/images (1).jpeg"),
            ),
          ],
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
                  child: Text("View all", style: TextStyle(color: Colors.blue)),
                ),
              ],
            ),
            SizedBox(height: 10),
            Column(
              children: List.generate(4, (index) => _buildCommunityItem()),
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

  Widget _buildCommunityItem() {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: AssetImage("assets/Liverpool-logo.jpg"),
      ),
      title: Text("weCode", style: TextStyle(fontWeight: FontWeight.bold)),
      subtitle: Text("23K members - Where Code Comes Alive"),
      trailing: ElevatedButton(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.blue,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        child: Text("Join", style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildServiceItems(BuildContext context) {
    final services = [
      "Book a Tutor",
      "Groups",
      "Hobbies",
      "Games",
      "Marketplace",
      "Jobs"
    ];

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: services.map((service) {
        return SizedBox(
          width: 120,
          height: 100,
          child: GestureDetector(
            onTap: () {
              if (service == "Book a Tutor") {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => BookTutorScreen()),
                );
              }
            },
            child: Card(
              color: Colors.white,
              child: Center(child: Text(service)),
            ),
          ),
        );
      }).toList(),
    );
  }
}
