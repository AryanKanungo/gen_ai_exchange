import 'package:flutter/material.dart';

class CommunityCornerCard extends StatelessWidget {
  const CommunityCornerCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Card(
        color: Colors.yellow[300],
        elevation: 1, // Adds a subtle shadow for a card-like effect
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          leading: const Icon(
            Icons.group, // Community icon
            color: Color(0xFF7695FF),
            size: 30,
          ),
          title: const Text(
            'Community Corner',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          trailing: const Icon(
            Icons.arrow_forward_ios, // Right arrow icon
            color: Colors.black54,
            size: 18,
          ),
          onTap: () {
            // Add your navigation logic here to open the community section
            // For example: Navigator.push(context, MaterialPageRoute(builder: (context) => CommunityScreen()));
          },
        ),
      ),
    );
  }
}