# Flutter App Setup Guide

## Quick Setup

### 1. Install Flutter Dependencies
```bash
cd client
flutter pub get
```

### 2. Configure API Settings
Edit `lib/config/app_config.dart` and update:

```dart
// Change this to your API server URL
static const String apiBaseUrl = 'http://localhost:8000';

// Replace with your actual API key
static const String apiKey = 'your-api-key-here';
```

### 3. Run the App
```bash
flutter run
```

## Configuration Options

### API Configuration
- `apiBaseUrl`: Your FastAPI server URL (default: http://localhost:8000)
- `apiKey`: Your API key for authentication

### File Upload Settings
- `allowedFileExtensions`: Supported file types (jpg, jpeg, png, gif, pdf)
- `maxFileSizeMB`: Maximum file size limit (default: 10MB)

### Polling Configuration
- `pollingIntervalSeconds`: How often to check status (default: 2 seconds)
- `maxPollingAttempts`: Maximum polling attempts (default: 300 = 10 minutes)

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure your FastAPI server is running
   - Check the `apiBaseUrl` in `app_config.dart`
   - Verify network connectivity

2. **File Upload Fails**
   - Check file size (max 10MB)
   - Ensure file format is supported
   - Verify API key is correct

3. **App Won't Start**
   - Run `flutter doctor` to check Flutter installation
   - Ensure all dependencies are installed: `flutter pub get`
   - Check for any syntax errors in the code

### Debug Mode
```bash
flutter run --debug
```

### Clean Build
```bash
flutter clean
flutter pub get
flutter run
```

## Platform-Specific Notes

### Android
- Requires Android SDK and emulator/device
- Internet permission is automatically added
- File access permissions are handled by file_picker

### iOS
- Requires Xcode and iOS Simulator/device
- May need to configure network security settings

### Web
- Runs in any modern browser
- File upload works with browser's file picker
- No additional setup required 