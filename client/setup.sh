#!/bin/bash

# Flutter Setup Script for Math Homework Client
echo "Setting up Flutter Math Homework Client..."

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter first."
    echo "   Visit: https://docs.flutter.dev/get-started/install"
    exit 1
fi

echo "✅ Flutter is installed"

# Check Flutter doctor
echo "📋 Running Flutter doctor..."
flutter doctor

# Get dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get

# Check if the dependencies were installed successfully
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run code generation (if needed in the future)
# flutter packages pub run build_runner build

echo "🎉 Setup complete! You can now run the app with:"
echo "   flutter run"
echo ""
echo "📱 Make sure you have:"
echo "   - A device connected or emulator running"
echo "   - The backend server running at the configured URL"
echo ""
echo "🔧 To configure the backend URL, edit:"
echo "   lib/config/app_config.dart"
