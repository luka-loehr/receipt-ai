#!/usr/bin/env python3
"""
Unified Google API Test Script
Tests both Calendar and Gmail using the same credentials file
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def test_unified_google_apis():
    """Test both Google Calendar and Gmail APIs using unified credentials"""
    print("🔐 Unified Google API Test")
    print("=" * 40)
    print()
    
    # Use the unified credentials file for both APIs
    credentials_file = 'google_credentials.json'
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        return False
    
    print(f"✅ Using credentials file: {credentials_file}")
    print()
    
    # Test Calendar API
    print("📅 Testing Google Calendar API...")
    calendar_success = test_calendar_api(credentials_file)
    print()
    
    # Test Gmail API
    print("📧 Testing Gmail API...")
    gmail_success = test_gmail_api(credentials_file)
    print()
    
    # Summary
    print("📊 Test Results:")
    print(f"   Calendar API: {'✅ Working' if calendar_success else '❌ Failed'}")
    print(f"   Gmail API: {'✅ Working' if gmail_success else '❌ Failed'}")
    print()
    
    if calendar_success and gmail_success:
        print("🎉 All APIs working! You can now generate receipts with real data.")
        print("   Run: python morning_brief.py")
        return True
    else:
        print("⚠️  Some APIs failed. Check the errors above.")
        return False

def test_calendar_api(credentials_file):
    """Test Google Calendar API"""
    try:
        # OAuth2 scopes
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Get credentials
        creds = get_credentials(credentials_file, SCOPES, 'calendar_token.json')
        if not creds:
            return False
        
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's events
        from datetime import datetime, timedelta
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
        
        if not events:
            print("   📭 No events found for today")
        else:
            print(f"   ✅ Found {len(events)} events today:")
            for event in events[:3]:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if 'dateTime' in event['start']:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                else:
                    time_str = "All day"
                
                print(f"      • {event['summary']} at {time_str}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Calendar API test failed: {e}")
        return False

def test_gmail_api(credentials_file):
    """Test Gmail API"""
    try:
        # OAuth2 scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Get credentials
        creds = get_credentials(credentials_file, SCOPES, 'gmail_token.json')
        if not creds:
            return False
        
        # Build the service
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=3,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("   📭 No messages found in inbox")
        else:
            print(f"   ✅ Found {len(messages)} recent messages:")
            
            for i, message in enumerate(messages):
                msg = service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject']
                ).execute()
                
                headers = msg['payload']['headers']
                from_header = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject_header = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                
                # Clean up the from field
                from_name = from_header.split('<')[0].strip() if '<' in from_header else from_header
                
                print(f"      {i+1}. From: {from_name}")
                print(f"         Subject: {subject_header[:40]}{'...' if len(subject_header) > 40 else ''}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Gmail API test failed: {e}")
        return False

def get_credentials(credentials_file, scopes, token_file):
    """Get OAuth2 credentials for the specified scopes"""
    creds = None
    
    # Check if we have a valid token file
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception as e:
            print(f"   ⚠️  Could not load existing token: {e}")
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"   ⚠️  Could not refresh token: {e}")
                creds = None
        
        if not creds:
            try:
                print("   🌐 Starting OAuth2 authorization...")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                
                print("   ✅ Authorization completed!")
                
            except Exception as e:
                print(f"   ❌ Authorization failed: {e}")
                return None
    
    return creds

if __name__ == "__main__":
    success = test_unified_google_apis()
    
    if not success:
        print("❌ Some tests failed. Please check the errors above.")
        print("   Make sure you have enabled both Calendar and Gmail APIs in Google Cloud Console.")
