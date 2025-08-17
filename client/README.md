# Math Homework Client

A Flutter mobile application for the Math Homework Backend that allows users to upload images or PDFs of math problems and receive step-by-step solutions.

## Features

- 📸 **Take photos** of math problems using the camera
- 📁 **Upload files** (images and PDFs) from device storage
- 🔄 **Real-time processing** with status updates
- 📝 **Step-by-step solutions** with detailed explanations
- 📱 **Clean, intuitive UI** optimized for mobile devices
- 📊 **Problem history** to review past solutions

## Prerequisites

- Flutter SDK (3.0.0 or later)
- Dart SDK
- Android Studio / Xcode for mobile development
- Running Math Homework Backend server

## Setup

1. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

2. **Configure Backend URL:**
   Edit `lib/services/math_service.dart` and update the `baseUrl` to match your backend server:
   ```dart
   static const String baseUrl = 'http://your-backend-url:8000/api/v1';
   ```

3. **Run the app:**
   ```bash
   # For development
   flutter run
   
   # For Android
   flutter run -d android
   
   # For iOS
   flutter run -d ios
   ```

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/
│   └── math_problem.dart     # Data models
├── screens/
│   ├── home_screen.dart      # Main upload screen
│   └── result_screen.dart    # Solution display screen
├── services/
│   └── math_service.dart     # API service layer
└── widgets/
    ├── upload_button.dart    # Custom upload button
    ├── problem_card.dart     # Problem list item
    └── solution_step.dart    # Solution step display
```

## Dependencies

- **http**: HTTP client for API calls
- **file_picker**: File selection from device storage
- **image_picker**: Camera integration for photo capture
- **provider**: State management
- **permission_handler**: Runtime permissions
- **flutter_pdfview**: PDF viewing capabilities
- **flutter_spinkit**: Loading indicators
- **flutter_math_fork**: Math equation rendering

## API Integration

The app integrates with the FastAPI backend through the following endpoints:

- `POST /api/v1/problems/upload` - Upload files
- `GET /api/v1/problems/{id}` - Get problem status
- `GET /api/v1/problems` - List user problems

## Permissions

### Android
- `INTERNET` - Network access
- `CAMERA` - Camera access for photos
- `READ_EXTERNAL_STORAGE` - File access
- `WRITE_EXTERNAL_STORAGE` - File storage

### iOS
- Camera usage description
- Photo library usage description

## Building for Production

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## Configuration

### Backend URL Configuration
Update the backend URL in `lib/services/math_service.dart`:

```dart
static const String baseUrl = 'http://localhost:8000/api/v1'; // Development
// static const String baseUrl = 'https://your-domain.com/api/v1'; // Production
```

### Authentication (Future Enhancement)
The app is designed to support Firebase authentication. To implement:

1. Add Firebase configuration files
2. Update API service to include authentication headers
3. Add login/logout screens

## Troubleshooting

### Common Issues

1. **Network Connection Errors**
   - Ensure backend server is running
   - Check firewall settings
   - Verify correct backend URL

2. **File Upload Failures**
   - Check file size limits
   - Verify supported file formats (JPG, PNG, PDF)
   - Ensure proper permissions

3. **Camera/Gallery Access**
   - Grant camera and storage permissions
   - Check device compatibility

### Debug Mode
Run with verbose logging:
```bash
flutter run --verbose
```

## Contributing

1. Follow Flutter coding conventions
2. Use meaningful commit messages
3. Test on both Android and iOS
4. Update documentation for new features

## License

This project is part of the Math Homework Backend system.
