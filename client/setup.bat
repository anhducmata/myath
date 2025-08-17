@echo off
echo Setting up Flutter Math Homework Client...

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flutter is not installed. Please install Flutter first.
    echo    Visit: https://docs.flutter.dev/get-started/install
    pause
    exit /b 1
)

echo ✅ Flutter is installed

REM Check Flutter doctor
echo 📋 Running Flutter doctor...
flutter doctor

REM Get dependencies
echo 📦 Getting Flutter dependencies...
flutter pub get

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo 🎉 Setup complete! You can now run the app with:
echo    flutter run
echo.
echo 📱 Make sure you have:
echo    - A device connected or emulator running
echo    - The backend server running at the configured URL
echo.
echo 🔧 To configure the backend URL, edit:
echo    lib/config/app_config.dart

pause
