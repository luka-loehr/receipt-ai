#!/usr/bin/env python3
"""
🚀 Receipt Printer - Complete Setup Script
One script to set up everything and get you running immediately!
"""

import os
import json
import webbrowser
from pathlib import Path

def print_header():
    """Print beautiful header"""
    print("🚀" + "="*50 + "🚀")
    print("    RECEIPT PRINTER - COMPLETE SETUP")
    print("🚀" + "="*50 + "🚀")
    print()

def check_google_credentials():
    """Check if google_credentials.json exists"""
    if os.path.exists('google_credentials.json'):
        print("✅ google_credentials.json found in root directory")
        print("   Make sure you have enabled these APIs in Google Cloud Console:")
        print("   - Gmail API")
        print("   - Google Calendar API") 
        print("   - Google Tasks API")
        print("   Visit: https://console.developers.google.com/apis")
        return True
    else:
        print("❌ google_credentials.json not found")
        print("   Please download it from Google Cloud Console and place it here")
        return False

def setup_openweather():
    """Get OpenWeatherMap API key"""
    print("\n🌤️  OpenWeatherMap API Setup")
    print("-" * 30)
    
    api_key = input("Enter your OpenWeatherMap API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        update_env_file('OPENWEATHER_API_KEY', api_key)
        print("✅ OpenWeatherMap API key saved!")
        return True
    else:
        print("⏭️  Skipped OpenWeatherMap setup")
        return False

def setup_openai():
    """Get OpenAI API key"""
    print("\n🤖 OpenAI API Setup")
    print("-" * 30)
    
    print("📋 To get your OpenAI API key:")
    print("   1. Go to: https://platform.openai.com/api-keys")
    print("   2. Sign in to your OpenAI account (or create one)")
    print("   3. Click 'Create new secret key'")
    print("   4. Give it a name (e.g., 'Receipt Printer')")
    print("   5. Copy the key (starts with 'sk-')")
    print("   6. ⚠️  Keep it secure - you won't see it again!")
    print()
    
    print("💰 Pricing info:")
    print("   • GPT-4o: ~$0.005 per 1K input tokens, ~$0.015 per 1K output tokens")
    print("   • Morning brief: ~$0.01-0.02 per generation")
    print("   • Set usage limits at: https://platform.openai.com/usage")
    print()
    
    # Offer to open browser
    open_browser = input("Open OpenAI API keys page in browser? (y/n): ").lower().strip()
    if open_browser == 'y':
        try:
            webbrowser.open('https://platform.openai.com/api-keys')
            print("🌐 Browser opened!")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    print()
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Validate API key format
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
            confirm = input("Continue anyway? (y/n): ").lower().strip()
            if confirm != 'y':
                print("⏭️  Skipped OpenAI setup")
                return False
        
        # Update .env file
        update_env_file('OPENAI_API_KEY', api_key)
        print("✅ OpenAI API key saved!")
        
        # Test the API key
        if test_openai_api(api_key):
            print("✅ OpenAI API key is working!")
            return True
        else:
            print("❌ OpenAI API key test failed")
            return False
    else:
        print("⏭️  Skipped OpenAI setup")
        return False

def test_openai_api(api_key):
    """Test OpenAI API key"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, API test successful!' in German."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"   🤖 API Response: {result}")
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        return False

def setup_google_oauth():
    """Set up Google OAuth for Gmail and Calendar"""
    print("\n🔐 Google OAuth Setup")
    print("-" * 30)
    
    if not check_google_credentials():
        print("❌ Cannot proceed without google_credentials.json")
        return False
    
    print("📋 This will:")
    print("   1. Open your browser for Google authorization")
    print("   2. Generate tokens for Gmail and Calendar access")
    print("   3. Save tokens locally for future use")
    print()
    
    proceed = input("Proceed with OAuth setup? (y/n): ").lower().strip()
    if proceed != 'y':
        print("⏭️  Skipped OAuth setup")
        return False
    
    try:
        print("\n🌐 Opening browser for Google authorization...")
        
        # Test Calendar API first
        print("📅 Testing Calendar API...")
        if test_calendar_api():
            print("✅ Calendar API working!")
        else:
            print("❌ Calendar API failed")
            return False
        
        # Test Gmail API
        print("📧 Testing Gmail API...")
        if test_gmail_api():
            print("✅ Gmail API working!")
        else:
            print("❌ Gmail API failed")
            return False
        
        print("\n🎉 Google OAuth setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        return False

def test_calendar_api():
    """Test Google Calendar API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Get credentials
        creds = None
        if os.path.exists('calendar_token.json'):
            creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('calendar_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Test the API
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's events
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   📅 Found {len(events)} events today")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Calendar API error: {e}")
        return False

def test_gmail_api():
    """Test Gmail API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Get credentials
        creds = None
        if os.path.exists('gmail_token.json'):
            creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Test the API
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        results = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = results.get('messages', [])
        
        print(f"   📧 Found {len(messages)} recent messages")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Gmail API error: {e}")
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

def create_env_template():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        
        # Copy from config.env.example
        if os.path.exists('config.env.example'):
            with open('config.env.example', 'r') as f:
                template_content = f.read()
            
            # Update with unified credentials
            template_content = template_content.replace(
                'GMAIL_CREDENTIALS_FILE=gmail_credentials.json',
                'GOOGLE_CREDENTIALS_FILE=google_credentials.json'
            )
            template_content = template_content.replace(
                'CALENDAR_CREDENTIALS_FILE=calendar_credentials.json',
                'GOOGLE_CREDENTIALS_FILE=google_credentials.json'
            )
            
            with open('.env', 'w') as f:
                f.write(template_content)
            
            print("✅ .env file created!")
        else:
            print("⚠️  config.env.example not found, creating basic .env")
            basic_env = """# Receipt Printer Configuration
GOOGLE_CREDENTIALS_FILE=google_credentials.json
USER_NAME=Luka
USER_TIMEZONE=Europe/Berlin
WEATHER_LOCATION=Karlsruhe,DE
MAX_EMAILS_TO_PROCESS=10
EMAIL_PRIORITY_KEYWORDS=urgent,important,asap,deadline,meeting
EMAIL_SPAM_FILTERS=newsletter,marketing,promotion,unsubscribe

# API Keys (set these during setup)
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
"""
            with open('.env', 'w') as f:
                f.write(basic_env)
            print("✅ Basic .env file created!")

def final_test():
    """Run final test to ensure everything works"""
    print("\n🧪 Final System Test")
    print("-" * 20)
    
    try:
        # Test data services
        from data_services import DataManager
        
        print("📊 Testing data services...")
        manager = DataManager()
        
        # Test the new structured daily brief
        brief_response = manager.get_daily_brief()
        
        print(f"✅ Greeting: {brief_response.greeting}")
        print(f"✅ Brief: {brief_response.brief[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Final test failed: {e}")
        print("   This might be due to missing API keys or credentials")
        return False

def main():
    """Main setup function"""
    print_header()
    
    print("🎯 This setup will configure your Receipt Printer for:")
    print("   • OpenWeatherMap API (weather data)")
    print("   • OpenAI GPT-4o API (AI insights & greetings)")
    print("   • Google OAuth (Gmail & Calendar)")
    print()
    
    # Create .env file if it doesn't exist
    create_env_template()
    
    # Setup OpenWeatherMap
    setup_openweather()
    
    # Setup OpenAI
    setup_openai()
    
    # Setup Google OAuth
    setup_google_oauth()
    
    # Final test
    if final_test():
        print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print("✅ Your Receipt Printer is ready to use!")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python daily_brief.py")
        print("   2. Enjoy your personalized German daily brief!")
        print()
        print("📚 Need help? Check README.md for usage instructions")
    else:
        print("\n⚠️  Setup completed with some issues")
        print("   Check the errors above and try again")

if __name__ == "__main__":
    main()
