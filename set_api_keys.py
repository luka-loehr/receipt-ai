#!/usr/bin/env python3
"""
🔑 Quick API Key Setup Script
Simple script to set your API keys for the Receipt Printer
"""

import os
from pathlib import Path

def set_api_key(key_name, description, url, example_format=""):
    """Helper function to set an API key"""
    print(f"\n🔑 {key_name} Setup")
    print("-" * 40)
    print(f"📋 {description}")
    if url:
        print(f"🌐 Get your key at: {url}")
    if example_format:
        print(f"📝 Example format: {example_format}")
    print()
    
    api_key = input(f"Enter your {key_name} (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        update_env_file(key_name, api_key)
        print(f"✅ {key_name} saved!")
        return True
    else:
        print(f"⏭️  Skipped {key_name} setup")
        return False

def update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_file = '.env'
    
    # Read existing .env file
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Check if key already exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            key_exists = True
            break
    
    # Add new key if it doesn't exist
    if not key_exists:
        lines.append(f'{key}={value}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def main():
    """Main function"""
    print("🔑" + "="*50 + "🔑")
    print("    QUICK API KEY SETUP")
    print("🔑" + "="*50 + "🔑")
    print()
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Receipt Printer Configuration\n")
        print("✅ .env file created!")
    
    # Set API keys
    openai_set = set_api_key(
        "OPENAI_API_KEY",
        "Required for AI-generated greetings and briefs using GPT-4o",
        "https://platform.openai.com/api-keys",
        "sk-..."
    )
    
    openweather_set = set_api_key(
        "OPENWEATHER_API_KEY", 
        "Required for weather data (One Call API 3.0)",
        "https://openweathermap.org/api",
        "32-character string"
    )
    
    # Summary
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY")
    print("="*50)
    print(f"OpenAI API Key: {'✅ Set' if openai_set else '❌ Not set'}")
    print(f"OpenWeather API Key: {'✅ Set' if openweather_set else '❌ Not set'}")
    
    if openai_set and openweather_set:
        print("\n🎉 All API keys are set! You can now run:")
        print("   python3 morning_brief.py")
    else:
        print("\n⚠️  Some API keys are missing. Run this script again to set them.")
        print("   Or run the full setup: python3 setup.py")

if __name__ == "__main__":
    main()
