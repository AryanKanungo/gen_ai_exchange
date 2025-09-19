import 'package:artisans/screens/home/modules/communitycorner_card.dart';
import 'package:artisans/screens/home/modules/post_card.dart';
import 'package:flutter/material.dart';

import '../overall/appbar.dart';
import '../overall/drawer.dart';
import 'modules/learning_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(),
      drawer: CustomDrawer(),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
            PostCard(context),
              const SizedBox(height: 16),
              CommunityCornerCard(),
              SizedBox(height: 16),
              LearningSupportCard(),
            ],
          ),
        ),
      )
    );
  }
}
