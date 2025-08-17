# Development Guide

## Quick Start

### Prerequisites
1. Install Flutter SDK (3.0.0+)
2. Install Android Studio or Xcode
3. Ensure the backend server is running

### Setup
1. Run the setup script:
   - **Windows**: `setup.bat`
   - **macOS/Linux**: `./setup.sh`

2. Or manually:
   ```bash
   flutter pub get
   flutter doctor
   ```

### Development

#### Running the App
```bash
# Debug mode
flutter run

# Hot reload is enabled - save files to see changes instantly
```

#### Backend Configuration
Update `lib/config/app_config.dart`:
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator
// static const String baseUrl = 'http://localhost:8000/api/v1'; // iOS simulator
```

#### Testing
```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage
```

#### Building
```bash
# Android APK
flutter build apk --debug

# iOS (requires macOS)
flutter build ios --debug
```

## Architecture

### State Management
- Using **Provider** for state management
- Services are injected as providers in `main.dart`

### API Layer
- `MathService` handles all backend communication
- Automatic retry logic for failed requests
- Progress tracking for long-running operations

### UI Structure
```
screens/
├── home_screen.dart      # Main screen with upload options
└── result_screen.dart    # Solution display

widgets/
├── upload_button.dart    # Reusable upload button
├── problem_card.dart     # Problem list item
└── solution_step.dart    # Step-by-step solution display
```

## Development Tips

### Debugging
1. Enable verbose logging:
   ```bash
   flutter run --verbose
   ```

2. Use Flutter Inspector for UI debugging

3. Check backend connectivity:
   ```dart
   print('Backend URL: ${AppConfig.baseUrl}');
   ```

### Common Issues

#### Network Issues
- **Android Emulator**: Use `10.0.2.2` instead of `localhost`
- **iOS Simulator**: Use `localhost` or actual IP address
- **Physical Devices**: Use your computer's IP address

#### Permissions
- Add necessary permissions to `AndroidManifest.xml` and `Info.plist`
- Request runtime permissions for camera and storage

#### File Upload
- Check file size limits in backend
- Ensure proper MIME type handling
- Test with different file formats

### Code Style
- Follow Dart/Flutter conventions
- Use meaningful variable names
- Add comments for complex logic
- Keep widgets small and focused

### Performance
- Use `const` constructors where possible
- Avoid unnecessary rebuilds
- Optimize image loading and caching
- Handle large lists with pagination

## API Integration

### Upload Flow
1. User selects file or takes photo
2. File is uploaded to `/api/v1/problems/upload`
3. App polls `/api/v1/problems/{id}` for status
4. Solution is displayed when processing completes

### Error Handling
- Network errors are caught and displayed to user
- Timeouts are handled gracefully
- User can retry failed operations

## Deployment

### Android
1. Build signed APK:
   ```bash
   flutter build apk --release
   ```

2. Upload to Google Play Store

### iOS
1. Build for App Store:
   ```bash
   flutter build ios --release
   ```

2. Upload via Xcode or Application Loader

### Configuration for Production
1. Update `AppConfig.baseUrl` to production URL
2. Configure proper signing certificates
3. Test on real devices
4. Enable crash reporting (Firebase Crashlytics)

## Future Enhancements

### Planned Features
- [ ] User authentication (Firebase Auth)
- [ ] Offline mode with local storage
- [ ] Dark mode support
- [ ] Multiple language support
- [ ] Push notifications for completed solutions
- [ ] Solution sharing functionality
- [ ] Handwriting recognition improvement

### Technical Improvements
- [ ] Add comprehensive unit tests
- [ ] Implement integration tests
- [ ] Add performance monitoring
- [ ] Implement proper error tracking
- [ ] Add analytics for user behavior

## Contributing

1. Create feature branch
2. Write tests for new functionality
3. Ensure code follows style guidelines
4. Test on both platforms
5. Submit pull request with description

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Provider Package](https://pub.dev/packages/provider)
- [HTTP Package](https://pub.dev/packages/http)
