#!/usr/bin/env python3
"""
Simple Gmail Test Script
Tests the Gmail credentials and completes OAuth2 authorization
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def test_gmail():
    """Test Gmail API connection"""
    print("📧 Testing Gmail API...")
    print()
    
    # OAuth2 scopes - read-only access to Gmail
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    
    # Check if we have a valid token file
    if os.path.exists('gmail_token.json'):
        print("🔑 Loading existing authorization token...")
        creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
    
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
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
            
            print("✅ Authorization completed!")
            print("   Token saved for future use")
    
    print()
    print("🔍 Testing Gmail API connection...")
    
    try:
        # Build the service
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        print("📬 Fetching recent emails...")
        
        results = service.users().messages().list(
            userId='me', 
            maxResults=5,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("   📭 No messages found in inbox")
        else:
            print(f"   ✅ Found {len(messages)} recent messages:")
            
            for i, message in enumerate(messages[:3]):  # Show first 3
                msg = service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg['payload']['headers']
                from_header = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject_header = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_header = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Clean up the from field (remove email part if it's there)
                from_name = from_header.split('<')[0].strip() if '<' in from_header else from_header
                
                print(f"      {i+1}. From: {from_name}")
                print(f"         Subject: {subject_header[:50]}{'...' if len(subject_header) > 50 else ''}")
                print(f"         Date: {date_header[:25]}")
                print()
        
        print("🎉 Gmail API test successful!")
        print("   Your Gmail integration is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Gmail Integration Test")
    print("=" * 35)
    print()
    
    success = test_gmail()
    
    print()
    if success:
        print("✅ Setup complete! You can now generate receipts with real Gmail data.")
        print("   Run: python morning_brief.py")
    else:
        print("❌ Setup failed. Please check your credentials and try again.")
