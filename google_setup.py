#!/usr/bin/env python3
"""
Google API Setup Script
Helps configure Google Calendar and Gmail integration
"""

import os
import json
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header():
    """Print setup header"""
    print("🔐 Google API Setup for Receipt Printer")
    print("=" * 50)
    print()

def setup_google_calendar():
    """Guide user through Google Calendar setup"""
    print("📅 Google Calendar Setup")
    print("-" * 30)
    print()
    
    print("Step 1: Go to Google Cloud Console")
    print("   🌐 Visit: https://console.cloud.google.com/")
    print("   👤 Sign in with your Google account")
    print()
    
    print("Step 2: Create/Select Project")
    print("   📁 Create a new project or select existing one")
    print("   💡 Project name: 'Receipt Printer' (or any name you prefer)")
    print()
    
    print("Step 3: Enable Google Calendar API")
    print("   🔍 Go to 'APIs & Services' → 'Library'")
    print("   🔍 Search for 'Google Calendar API'")
    print("   ✅ Click 'Enable'")
    print()
    
    print("Step 4: Create OAuth2 Credentials")
    print("   🔑 Go to 'APIs & Services' → 'Credentials'")
    print("   ➕ Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("   💻 Choose 'Desktop application'")
    print("   📝 Name: 'Receipt Printer'")
    print("   💾 Download as 'google_credentials.json'")
    print()
    
    print("Step 5: Place the File")
    print("   📁 Put 'google_credentials.json' in this directory")
    print()
    
    # Check if credentials file exists
    if os.path.exists('google_credentials.json'):
        print("✅ google_credentials.json found!")
        print("   Testing credentials...")
        test_calendar_credentials()
    else:
        print("❌ google_credentials.json not found")
        print("   Please follow the steps above and place the file here")
        print()
        
        # Offer to open Google Cloud Console
        open_console = input("Open Google Cloud Console in browser? (y/n): ").lower()
        if open_console == 'y':
            webbrowser.open('https://console.cloud.google.com/')

def setup_gmail():
    """Guide user through Gmail setup"""
    print("📧 Gmail Setup")
    print("-" * 20)
    print()
    
    print("⚠️  Note: Gmail setup is more complex and requires careful OAuth2 configuration")
    print()
    
    print("Step 1: Go to Google Cloud Console")
    print("   🌐 Visit: https://console.cloud.google.com/")
    print("   👤 Sign in with your Google account")
    print()
    
    print("Step 2: Create/Select Project")
    print("   📁 Create a new project or select existing one")
    print()
    
    print("Step 3: Enable Gmail API")
    print("   🔍 Go to 'APIs & Services' → 'Library'")
    print("   🔍 Search for 'Gmail API'")
    print("   ✅ Click 'Enable'")
    print()
    
    print("Step 4: Create OAuth2 Credentials")
    print("   🔑 Go to 'APIs & Services' → 'Credentials'")
    print("   ➕ Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("   💻 Choose 'Desktop application'")
    print("   📝 Name: 'Receipt Printer'")
    print("   💾 Download as 'google_credentials.json'")
    print()
    
    print("Step 5: Configure OAuth Consent Screen")
    print("   ⚠️  Important: You may need to configure OAuth consent screen")
    print("   🔒 Go to 'OAuth consent screen' tab")
    print("   👥 Choose 'External' user type")
    print("   📧 Add your email as test user")
    print()
    
    print("Step 6: Place the File")
    print("   📁 Put 'google_credentials.json' in this directory")
    print()
    
    # Check if credentials file exists
    if os.path.exists('google_credentials.json'):
        print("✅ google_credentials.json found!")
        print("   Testing credentials...")
        test_gmail_credentials()
    else:
        print("❌ google_credentials.json not found")
        print("   Please follow the steps above and place the file here")
        print()
        
        # Offer to open Google Cloud Console
        open_console = input("Open Google Cloud Console in browser? (y/n): ").lower()
        if open_console == 'y':
            webbrowser.open('https://console.cloud.google.com/')

def test_calendar_credentials():
    """Test Google Calendar credentials"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # Load credentials
        with open('google_credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Set up OAuth2 flow
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
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
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        print(f"✅ Calendar API working! Found {len(events)} events today")
        if events:
            print("   Sample events:")
            for event in events[:3]:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"   - {event['summary']} at {start}")
        
    except Exception as e:
        print(f"❌ Calendar API test failed: {e}")
        print("   This is normal for first-time setup - you'll need to authorize the app")

def test_gmail_credentials():
    """Test Gmail credentials"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # Load credentials
        with open('google_credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Set up OAuth2 flow
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
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
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        
        print(f"✅ Gmail API working! Found {len(messages)} recent messages")
        
    except Exception as e:
        print(f"❌ Gmail API test failed: {e}")
        print("   This is normal for first-time setup - you'll need to authorize the app")

def main():
    """Main setup function"""
    print_header()
    
    print("Choose which service to set up:")
    print("1. Google Calendar (Recommended - easier)")
    print("2. Gmail (More complex, but powerful)")
    print("3. Both")
    print("4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        setup_google_calendar()
    elif choice == '2':
        setup_gmail()
    elif choice == '3':
        print("Setting up both services...")
        print()
        setup_google_calendar()
        print()
        setup_gmail()
    elif choice == '4':
        print("Setup cancelled.")
        return
    else:
        print("Invalid choice. Please run the script again.")
        return
    
    print()
    print("🎉 Setup complete!")
    print()
    print("Next steps:")
    print("1. Follow the setup instructions above")
    print("2. Place credential files in this directory")
    print("3. Run this script again to test")
    print("4. Generate receipts with real data!")

if __name__ == "__main__":
    main()
