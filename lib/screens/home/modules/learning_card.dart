import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class LearningSupportCard extends StatefulWidget {
  const LearningSupportCard({super.key});

  @override
  State<LearningSupportCard> createState() => _LearningSupportCardState();
}

class _LearningSupportCardState extends State<LearningSupportCard> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Map<String, dynamic>> topics = const [
    {
      'icon': Icons.camera_alt_outlined,
      'label': 'Photograph Your Craft',
    },
    {
      'icon': Icons.attach_money_outlined,
      'label': 'Pricing Tips',
    },
    {
      'icon': Icons.local_shipping_outlined,
      'label': 'Packaging for Orders',
    },
    {
      'icon': Icons.inventory_2_outlined,
      'label': 'Inventory Management',
    },
    {
      'icon': Icons.sell_outlined,
      'label': 'Marketing Your Work',
    },
  ];

  @override
  void initState() {
    super.initState();
    _pageController.addListener(() {
      setState(() {
        _currentPage = _pageController.page!.round();
      });
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const Color accentColor = Color(0xFFFFD66B);

    return Card(
      color: Color(0xFF4DA8DA),
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Learning & Support',
              style: GoogleFonts.poppins(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Color(0xFFF5F5F5),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 120,
              child: PageView.builder(
                controller: _pageController,
                itemCount: topics.length,
                itemBuilder: (context, index) {
                  final topic = topics[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: accentColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Icon(
                            topic['icon'],
                            color: accentColor,
                            size: 40,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Flexible(
                          child: Text(
                            topic['label'],
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: GoogleFonts.poppins().fontFamily,
                              color: const Color(0xFFF5F5F5),
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  topics.length,
                      (index) => AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    margin: const EdgeInsets.symmetric(horizontal: 4.0),
                    height: 8.0,
                    width: _currentPage == index ? 24.0 : 8.0,
                    decoration: BoxDecoration(
                      color: _currentPage == index ? accentColor : Colors.grey.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(4.0),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}