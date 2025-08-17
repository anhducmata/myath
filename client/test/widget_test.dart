import 'package:flutter_test/flutter_test.dart';
import 'package:math_homework_client/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the app starts with the correct title
    expect(find.text('Math Homework Helper'), findsOneWidget);

    // Verify that upload buttons are present
    expect(find.text('Pick File'), findsOneWidget);
    expect(find.text('Take Photo'), findsOneWidget);
  });
}
