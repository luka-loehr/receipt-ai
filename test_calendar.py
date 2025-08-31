#!/usr/bin/env python3
"""
Simple Google Calendar Test Script
Tests the calendar credentials and completes OAuth2 authorization
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def test_calendar():
    """Test Google Calendar API connection"""
    print("📅 Testing Google Calendar API...")
    print()
    
    # OAuth2 scopes - read-only access to calendar
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    creds = None
    
    # Check if we have a valid token file
    if os.path.exists('calendar_token.json'):
        print("🔑 Loading existing authorization token...")
        creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🌐 Starting OAuth2 authorization...")
            print("   This will open your browser for authorization")
            print()
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('calendar_token.json', 'w') as token:
                token.write(creds.to_json())
            
            print("✅ Authorization completed!")
            print("   Token saved for future use")
    
    print()
    print("🔍 Testing Calendar API connection...")
    
    try:
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's events
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        print(f"📅 Fetching events from {datetime.utcnow().strftime('%Y-%m-%d')}...")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("   📭 No events found for today")
        else:
            print(f"   ✅ Found {len(events)} events today:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if 'dateTime' in event['start']:
                    # Convert to readable time
                    from datetime import datetime
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                else:
                    time_str = "All day"
                
                print(f"      • {event['summary']} at {time_str}")
        
        print()
        print("🎉 Calendar API test successful!")
        print("   Your calendar integration is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Calendar API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Google Calendar Integration Test")
    print("=" * 40)
    print()
    
    success = test_calendar()
    
    print()
    if success:
        print("✅ Setup complete! You can now generate receipts with real calendar data.")
        print("   Run: python morning_brief.py")
    else:
        print("❌ Setup failed. Please check your credentials and try again.")
