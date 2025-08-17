# Math Problem Solver - Flutter App

A Flutter application that allows users to upload math problem images or PDFs and receive solutions through an API.

## Features

- 📁 File upload (JPG, PNG, GIF, PDF)
- 🔄 Real-time status polling
- 📊 Progress tracking
- ✅ Solution display
- 🎨 Modern Material Design UI

## Setup

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Android Studio / VS Code with Flutter extensions

### Installation

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Configure API settings:
   - Open `lib/services/api_service.dart`
   - Update `baseUrl` to point to your API server
   - Replace `apiKey` with your actual API key

### Configuration

Before running the app, make sure to:

1. **Update API URL**: In `lib/services/api_service.dart`, change:
   ```dart
   static const String baseUrl = 'http://localhost:8000'; // Your API URL
   ```

2. **Set API Key**: Replace the placeholder API key:
   ```dart
   static const String apiKey = 'your-api-key-here'; // Your actual API key
   ```

## Running the App

### Development Mode
```bash
flutter run
```

### Build for Production

#### Android
```bash
flutter build apk --release
```

#### iOS
```bash
flutter build ios --release
```

#### Web
```bash
flutter build web --release
```

## Usage

1. **Upload File**: Tap the "Choose File" button to select a math problem image or PDF
2. **Monitor Progress**: The app will show real-time processing status
3. **View Solution**: Once processing is complete, the solution will be displayed
4. **Start Over**: Use the "Clear & Start Over" button to upload a new problem

## API Integration

The app integrates with the following API endpoints:

- `POST /problems` - Upload file and create problem
- `GET /problems/{problem_id}` - Get problem details
- `GET /problems/{problem_id}/task-status` - Get task processing status

## Project Structure

```
lib/
├── main.dart              # App entry point
├── models/
│   └── problem.dart       # Data models
├── providers/
│   └── api_provider.dart  # State management
├── screens/
│   └── home_screen.dart   # Main screen
├── services/
│   └── api_service.dart   # API communication
└── widgets/
    ├── status_card.dart   # Status display widget
    └── solution_display.dart # Solution display widget
```

## Dependencies

- `http`: HTTP requests
- `file_picker`: File selection
- `provider`: State management
- `path`: File path utilities

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure your API server is running and accessible
2. **File Upload Fails**: Check file size and format restrictions
3. **API Key Issues**: Verify your API key is correct and has proper permissions

### Debug Mode

Run with debug information:
```bash
flutter run --debug
```

## License

This project is part of the Math Problem Solver system. 