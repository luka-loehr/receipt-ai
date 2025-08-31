#!/usr/bin/env python3
"""
Setup Script for Receipt Printer
Helps configure API keys and generate OAuth credentials
"""

import os
import json
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    if os.path.exists('config.env.example'):
        # Copy template to .env
        with open('config.env.example', 'r') as f:
            template = f.read()
        
        with open('.env', 'w') as f:
            f.write(template)
        
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your actual API keys")
    else:
        print("❌ config.env.example not found")

def setup_openweather():
    """Guide user through OpenWeatherMap setup"""
    print("\n🌤️  OpenWeatherMap API Setup:")
    print("1. Go to: https://openweathermap.org/api")
    print("2. Sign up for a free account")
    print("3. Get your API key from your account")
    print("4. Add it to your .env file as OPENWEATHER_API_KEY")
    
    api_key = input("\nEnter your OpenWeatherMap API key (or press Enter to skip): ").strip()
    if api_key:
        update_env_var('OPENWEATHER_API_KEY', api_key)
        print("✅ OpenWeatherMap API key saved")
    else:
        print("⏭️  Skipped OpenWeatherMap setup")

def setup_gemini():
    """Guide user through Gemini API setup"""
    print("\n🤖 Google Gemini API Setup:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Create a new API key")
    print("4. Add it to your .env file as GEMINI_API_KEY")
    
    api_key = input("\nEnter your Gemini API key (or press Enter to skip): ").strip()
    if api_key:
        update_env_var('GEMINI_API_KEY', api_key)
        print("✅ Gemini API key saved")
    else:
        print("⏭️  Skipped Gemini setup")

def setup_gmail():
    """Guide user through Gmail API setup"""
    print("\n📧 Gmail API Setup:")
    print("This requires Google Cloud Console setup:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Gmail API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Download credentials as google_credentials.json")
    print("6. Place the file in this directory")
    
    # Check if credentials file exists
    if os.path.exists('google_credentials.json'):
        print("✅ Google credentials found")
    else:
        print("❌ google_credentials.json not found")
        print("   You can still use the app with mock data")

def setup_calendar():
    """Guide user through Google Calendar API setup"""
    print("\n📅 Google Calendar API Setup:")
    print("This requires Google Cloud Console setup:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Google Calendar API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Download credentials as google_credentials.json")
    print("6. Place the file in this directory")
    
    # Check if credentials file exists
    if os.path.exists('google_credentials.json'):
        print("✅ Google credentials found")
    else:
        print("❌ google_credentials.json not found")
        print("   You can still use the app with mock data")

def update_env_var(key, value):
    """Update a variable in .env file"""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run setup first.")
        return
    
    # Read current .env file
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update or add the variable
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'{key}={value}\n')
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.writelines(lines)

def test_apis():
    """Test configured APIs"""
    print("\n🧪 Testing APIs...")
    
    # Load environment variables
    load_dotenv()
    
    # Test weather API
    weather_key = os.getenv('OPENWEATHER_API_KEY')
    if weather_key and weather_key != 'your_openweather_api_key_here':
        print("✅ OpenWeatherMap API key configured")
    else:
        print("❌ OpenWeatherMap API key not configured")
    
    # Test Gemini API
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key != 'your_gemini_api_key_here':
        print("✅ Gemini API key configured")
    else:
        print("❌ Gemini API key not configured")
    
    # Test Gmail credentials
    if os.path.exists('google_credentials.json'):
        print("✅ Google credentials found")
    else:
        print("❌ Google credentials not found")
    
    # Test Calendar credentials
    if os.path.exists('google_credentials.json'):
        print("✅ Google credentials found")
    else:
        print("❌ Google credentials not found")

def main():
    """Main setup function"""
    print("🚀 Receipt Printer Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Setup each service
    setup_openweather()
    setup_gemini()
    setup_gmail()
    setup_calendar()
    
    # Test configuration
    test_apis()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Place OAuth credential files in this directory")
    print("3. Run: python morning_brief.py")
    print("4. Run: python receipt_preview.py")

if __name__ == "__main__":
    main()
