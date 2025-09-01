#!/usr/bin/env python3
"""
Data Services Module
Handles real-time data fetching for weather, emails, calendar, and AI summarization
"""

import os
import json
import datetime
import pytz
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class WeatherData:
    """Weather information structure"""
    temperature: str
    condition: str
    high: str
    low: str
    humidity: str
    wind_speed: str
    feels_like: str

@dataclass
class EmailData:
    """Email information structure"""
    sender: str
    subject: str
    summary: str
    priority: str
    time: str
    thread_id: str
    is_important: bool

@dataclass
class CalendarEvent:
    """Calendar event structure"""
    title: str
    start_time: str
    end_time: str
    location: str
    description: str
    is_all_day: bool

class WeatherService:
    """Handles weather data fetching from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.location = os.getenv('WEATHER_LOCATION', 'Berlin,DE')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            print("⚠️  Warning: No OpenWeatherMap API key found. Using mock data.")
    
    def get_current_weather(self) -> WeatherData:
        """Get current weather data - requires API key"""
        if not self.api_key:
            raise Exception("OpenWeatherMap API key required")
        
        # Get current weather
        current_url = f"{self.base_url}/weather"
        params = {
            'q': self.location,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(current_url, params=params, timeout=10)
        response.raise_for_status()
        current_data = response.json()
        
        # Get forecast for high/low
        forecast_url = f"{self.base_url}/forecast"
        forecast_response = requests.get(forecast_url, params=params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Extract high/low from today's forecast
        today_forecasts = [f for f in forecast_data['list'] 
                         if datetime.datetime.fromtimestamp(f['dt']).date() == datetime.date.today()]
        
        if today_forecasts:
            temps = [f['main']['temp'] for f in today_forecasts]
            high_temp = max(temps)
            low_temp = min(temps)
        else:
            high_temp = current_data['main']['temp']
            low_temp = current_data['main']['temp']
        
        return WeatherData(
            temperature=f"{round(current_data['main']['temp'])}°C",
            condition=current_data['weather'][0]['description'].title(),
            high=f"{round(high_temp)}°C",
            low=f"{round(low_temp)}°C",
            humidity=f"{current_data['main']['humidity']}%",
            wind_speed=f"{round(current_data['wind']['speed'] * 3.6, 1)} km/h",  # Convert m/s to km/h
            feels_like=f"{round(current_data['main']['feels_like'])}°C"
        )

class EmailService:
    """Handles Gmail data fetching and processing"""
    
    def __init__(self):
        # Use the unified Google credentials file
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google_credentials.json')
        self.max_emails = int(os.getenv('MAX_EMAILS_TO_PROCESS', '10'))
        self.priority_keywords = os.getenv('EMAIL_PRIORITY_KEYWORDS', 'urgent,important,asap,deadline,meeting').split(',')
        self.spam_filters = os.getenv('EMAIL_SPAM_FILTERS', 'newsletter,marketing,promotion,unsubscribe').split(',')
        
        # Check if credentials exist
        if not os.path.exists(self.credentials_file):
            print("⚠️  Warning: No Google credentials found. Using mock data.")
    
    def get_recent_emails(self) -> List[EmailData]:
        """Get recent emails - requires Google credentials"""
        if not os.path.exists(self.credentials_file):
            raise Exception("Google credentials file required")
        
        # Real Gmail API integration
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
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=self.max_emails,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        email_data = []
        
        for message in messages:
            msg = service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = msg['payload']['headers']
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse date and format time
            try:
                from email.utils import parsedate_to_datetime
                from datetime import datetime
                dt = parsedate_to_datetime(date_str)
                time_str = dt.strftime("%I:%M %p")
            except:
                time_str = "Unknown"
            
            # Determine priority and importance
            subject_lower = subject.lower()
            priority = "high" if any(keyword in subject_lower for keyword in self.priority_keywords) else "medium"
            is_important = any(keyword in subject_lower for keyword in self.priority_keywords)
            
            # Create summary (using subject for now, could be enhanced with AI)
            summary = subject[:100] + "..." if len(subject) > 100 else subject
            
            email_data.append(EmailData(
                sender=sender,
                subject=subject,
                summary=summary,
                priority=priority,
                time=time_str,
                thread_id=message['id'],
                is_important=is_important
            ))
        
        return email_data

class CalendarService:
    """Handles Google Calendar data fetching"""
    
    def __init__(self):
        # Use the unified Google credentials file
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google_credentials.json')
        self.timezone = os.getenv('USER_TIMEZONE', 'Europe/Berlin')
        
        if not os.path.exists(self.credentials_file):
            print("⚠️  Warning: No Google credentials found. Using mock data.")
    
    def get_upcoming_events(self) -> List[CalendarEvent]:
        """Get next 3 calendar events (today, tomorrow, day after) - requires Google credentials"""
        if not os.path.exists(self.credentials_file):
            raise Exception("Google credentials file required")
        
        # Real Google Calendar API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta
        import pytz
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Get credentials
        creds = None
        if os.path.exists('calendar_token.json'):
            creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('calendar_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Build Calendar service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get next 3 days of events
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z'
        
        print(f"   📅 Searching for events from {now} to {end}")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   📅 Found {len(events)} raw events from API")
        
        calendar_data = []
        
        for event in events:
            print(f"   📅 Processing event: {event.get('summary', 'No title')}")
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            if 'dateTime' in event['start']:
                # Time-specific event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                start_time = start_dt.strftime("%H:%M")
                end_time = end_dt.strftime("%H:%M")
                is_all_day = False
            else:
                # All-day event
                start_time = "Ganztägig"
                end_time = ""
                is_all_day = True
            
            calendar_data.append(CalendarEvent(
                title=event['summary'],
                start_time=start_time,
                end_time=end_time,
                location=event.get('location', ''),
                description=event.get('description', ''),
                is_all_day=is_all_day
            ))
        
        print(f"   📅 Returning {len(calendar_data)} processed events")
        return calendar_data

class AIService:
    """Handles AI-powered analysis and summarization using Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if not self.api_key:
            raise Exception("Gemini API key required")
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI service initialized successfully")
    
    def generate_comprehensive_brief(self, weather: WeatherData, emails: List[EmailData], events: List[CalendarEvent], user_name: str = "Luka") -> str:
        """Generate a comprehensive AI-powered German brief covering weather, important emails, and calendar events"""
        
        # Prepare data for AI analysis
        email_summaries = []
        for email in emails:
            email_summaries.append(f"Von: {email.sender}, Betreff: {email.subject}")
        
        event_summaries = []
        for event in events:
            event_summaries.append(f"{event.title} um {event.start_time}")
        
        prompt = f"""
        Erstelle einen kompakten, informativen Tagesüberblick AUF DEUTSCH für {user_name}. 
        
        Analysiere die E-Mails und erwähne nur die WICHTIGSTEN (z.B. von wichtigen Personen, dringende Themen, Termine).
        Ignoriere unwichtige E-Mails wie Newsletter, Notifications, etc.
        
        Wetter: {weather.temperature}, {weather.condition}
        
        E-Mails ({len(emails)} insgesamt):
        {chr(10).join(email_summaries)}
        
        Termine:
        {chr(10).join(event_summaries)}
        
        Erstelle einen fließenden deutschen Text (ca. 3-5 Sätze) der:
        1. Das Wetter kurz erwähnt
        2. NUR die wichtigsten E-Mails hervorhebt (nicht alle!)
        3. Die heutigen Termine auflistet
        4. Mit einer motivierenden Note endet
        
        Verwende keine Aufzählungen oder Emojis. Schreibe natürlich und freundlich.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip()

class DataManager:
    """Main data manager that coordinates all services"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.ai_service = AIService()
    
    def get_comprehensive_brief(self, user_name: str = "Luka") -> str:
        """Fetch all data and return AI-generated comprehensive brief"""
        print("🌤️  Fetching weather data...")
        weather = self.weather_service.get_current_weather()
        
        print("📧  Fetching email data...")
        emails = self.email_service.get_recent_emails()
        
        print("📅  Fetching calendar data...")
        events = self.calendar_service.get_upcoming_events()
        
        print("🤖  Generating AI brief...")
        brief = self.ai_service.generate_comprehensive_brief(weather, emails, events, user_name)
        
        return brief

if __name__ == "__main__":
    # Test the data services
    manager = DataManager()
    brief = manager.get_comprehensive_brief()
    
    print(f"\n🤖 AI Brief:")
    print(brief)
