#!/usr/bin/env python3
"""
Google Tasks API Enabler
Helps you enable the Google Tasks API in your Google Cloud Console
"""

import webbrowser
import os

def main():
    print("🔧 Google Tasks API Setup Helper")
    print("=" * 40)
    print()
    
    print("To use Google Tasks in your morning brief, you need to enable the Tasks API.")
    print()
    
    # Check if credentials file exists
    if os.path.exists('google_credentials.json'):
        print("✅ Found google_credentials.json")
        
        # Extract project ID from credentials (this is a simplified approach)
        try:
            import json
            with open('google_credentials.json', 'r') as f:
                creds = json.load(f)
                project_id = creds.get('project_id', 'Unknown')
                print(f"📁 Project ID: {project_id}")
        except:
            project_id = "your-project-id"
    else:
        print("❌ google_credentials.json not found")
        print("   Please run setup.py first to set up Google credentials")
        return
    
    print()
    print("📋 Steps to enable Google Tasks API:")
    print("1. Visit the Google Cloud Console")
    print("2. Select your project")
    print("3. Go to 'APIs & Services' > 'Library'")
    print("4. Search for 'Google Tasks API'")
    print("5. Click 'Enable'")
    print()
    
    # Offer to open the API library
    open_console = input("Open Google Cloud Console API Library? (y/n): ").lower().strip()
    if open_console == 'y':
        try:
            webbrowser.open('https://console.developers.google.com/apis/library')
            print("🌐 Opening Google Cloud Console...")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    print()
    print("🔗 Direct link to Tasks API:")
    print("https://console.developers.google.com/apis/api/tasks.googleapis.com/overview")
    print()
    
    print("💡 After enabling the API:")
    print("   - Wait a few minutes for changes to propagate")
    print("   - Run 'python3 daily_brief.py' again")
    print("   - The Tasks section will appear in your brief!")
    print()
    
    print("🎯 Your morning brief will now include:")
    print("   ✅ Weather data")
    print("   ✅ Email summaries") 
    print("   ✅ Calendar events")
    print("   ✅ Google Tasks with checkboxes")
    print("   ✅ AI-generated insights")

if __name__ == "__main__":
    main()
