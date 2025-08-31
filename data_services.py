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
        """Get current weather data"""
        if not self.api_key:
            return self._get_mock_weather()
        
        try:
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
            
        except Exception as e:
            print(f"⚠️  Weather API error: {e}. Using mock data.")
            return self._get_mock_weather()
    
    def _get_mock_weather(self) -> WeatherData:
        """Fallback mock weather data"""
        return WeatherData(
            temperature="22°C",
            condition="Partly Cloudy",
            high="26°C",
            low="18°C",
            humidity="65%",
            wind_speed="12 km/h",
            feels_like="24°C"
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
        """Get recent emails with AI-powered analysis"""
        if not os.path.exists(self.credentials_file):
            return self._get_mock_emails()
        
        try:
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
            
        except Exception as e:
            print(f"⚠️  Gmail API error: {e}. Using mock data.")
            return self._get_mock_emails()
    
    def _get_mock_emails(self) -> List[EmailData]:
        """Fallback mock email data"""
        return [
            EmailData(
                sender="Team Slack",
                subject="Weekly product sync notes",
                summary="Q3 roadmap on track. New feature launch delayed by 1 week. Customer feedback positive.",
                priority="high",
                time="8:45 AM",
                thread_id="mock_1",
                is_important=True
            ),
            EmailData(
                sender="Sarah Chen",
                subject="Re: Project timeline",
                summary="Confirmed meeting for Tuesday 2pm. Need final designs by EOW.",
                priority="high",
                time="9:12 AM",
                thread_id="mock_2",
                is_important=True
            ),
            EmailData(
                sender="GitHub",
                subject="3 new PRs ready for review",
                summary="Frontend refactor PR merged. Two backend PRs awaiting your review.",
                priority="medium",
                time="7:30 AM",
                thread_id="mock_3",
                is_important=False
            ),
            EmailData(
                sender="Calendar",
                subject="Today: 4 meetings scheduled",
                summary="10am Standup • 11am Client call • 2pm Design review • 4pm 1-on-1",
                priority="high",
                time="6:00 AM",
                thread_id="mock_4",
                is_important=True
            )
        ]

class CalendarService:
    """Handles Google Calendar data fetching"""
    
    def __init__(self):
        # Use the unified Google credentials file
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google_credentials.json')
        self.timezone = os.getenv('USER_TIMEZONE', 'Europe/Berlin')
        
        if not os.path.exists(self.credentials_file):
            print("⚠️  Warning: No Google credentials found. Using mock data.")
    
    def get_today_events(self) -> List[CalendarEvent]:
        """Get today's calendar events"""
        if not os.path.exists(self.credentials_file):
            return self._get_mock_events()
        
        try:
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
            
            # Get today's events - use exact same logic as the test
            now = datetime.utcnow().isoformat() + 'Z'
            end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
            
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
            
        except Exception as e:
            print(f"⚠️  Calendar API error: {e}. Using mock data.")
            return self._get_mock_events()
    
    def _get_mock_events(self) -> List[CalendarEvent]:
        """Fallback mock calendar data"""
        return [
            CalendarEvent(
                title="Daily Standup",
                start_time="10:00 AM",
                end_time="10:15 AM",
                location="Zoom",
                description="Team sync on daily progress",
                is_all_day=False
            ),
            CalendarEvent(
                title="Client Call",
                start_time="11:00 AM",
                end_time="12:00 PM",
                location="Google Meet",
                description="Project review with client",
                is_all_day=False
            ),
            CalendarEvent(
                title="Design Review",
                start_time="2:00 PM",
                end_time="3:00 PM",
                location="Conference Room A",
                description="Review new UI designs",
                is_all_day=False
            ),
            CalendarEvent(
                title="1-on-1 with Manager",
                start_time="4:00 PM",
                end_time="4:30 PM",
                location="Office",
                description="Weekly check-in",
                is_all_day=False
            )
        ]

class AIService:
    """Handles AI-powered analysis and summarization using Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI service initialized successfully")
            except Exception as e:
                print(f"⚠️  Gemini AI initialization error: {e}")
        else:
            print("⚠️  Warning: No Gemini API key found. AI features disabled.")
    
    def analyze_emails(self, emails: List[EmailData]) -> List[EmailData]:
        """Use AI to analyze email importance and generate summaries"""
        if not self.model:
            return emails
        
        try:
            # Prepare email data for AI analysis
            email_texts = []
            for email in emails:
                email_texts.append(f"From: {email.sender}\nSubject: {email.subject}\nContent: {email.summary}")
            
            combined_text = "\n\n---\n\n".join(email_texts)
            
            prompt = f"""
            Analyze these emails and for each one:
            1. Determine if it's important (high/medium/low priority)
            2. Generate a concise 1-2 sentence summary
            3. Identify if it requires immediate action
            
            Emails:
            {combined_text}
            
            Return your analysis in this exact format:
            EMAIL_1: priority=high|medium|low, summary="your summary here", action_required=true|false
            EMAIL_2: priority=high|medium|low, summary="your summary here", action_required=true|false
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response and update emails
            # This is a simplified parser - you might want to make it more robust
            lines = response.text.strip().split('\n')
            for i, line in enumerate(lines):
                if i < len(emails) and 'priority=' in line:
                    if 'priority=high' in line:
                        emails[i].priority = 'high'
                    elif 'priority=medium' in line:
                        emails[i].priority = 'medium'
                    else:
                        emails[i].priority = 'low'
                    
                    # Extract summary if provided
                    if 'summary=' in line:
                        summary_start = line.find('summary="') + 9
                        summary_end = line.find('"', summary_start)
                        if summary_start > 8 and summary_end > summary_start:
                            emails[i].summary = line[summary_start:summary_end]
            
            return emails
            
        except Exception as e:
            print(f"⚠️  AI analysis error: {e}. Using original email data.")
            return emails
    
    def generate_daily_insights(self, weather: WeatherData, emails: List[EmailData], events: List[CalendarEvent]) -> str:
        """Generate AI-powered daily insights in German"""
        if not self.model:
            return "Hab einen produktiven Tag!"
        
        try:
            prompt = f"""
            Based on this daily information, provide a motivational quote or insight for the day IN GERMAN:
            
            Weather: {weather.temperature}, {weather.condition}
            Emails: {len(emails)} new, {sum(1 for e in emails if e.priority == 'high')} urgent
            Events: {len(events)} meetings today
            
            Provide a brief, motivational insight or quote in German that's relevant to this day's schedule.
            Keep it under 100 characters and make it inspiring. Write ONLY in German.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️  AI insights error: {e}")
            return "Hab einen produktiven Tag!"

class DataManager:
    """Main data manager that coordinates all services"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.ai_service = AIService()
    
    def get_all_data(self) -> Tuple[WeatherData, List[EmailData], List[CalendarEvent], str]:
        """Fetch all data and return processed results"""
        print("🌤️  Fetching weather data...")
        weather = self.weather_service.get_current_weather()
        
        print("📧  Fetching email data...")
        emails = self.email_service.get_recent_emails()
        
        print("📅  Fetching calendar data...")
        events = self.calendar_service.get_today_events()
        
        print("🤖  Analyzing with AI...")
        emails = self.ai_service.analyze_emails(emails)
        insights = self.ai_service.generate_daily_insights(weather, emails, events)
        
        return weather, emails, events, insights

if __name__ == "__main__":
    # Test the data services
    manager = DataManager()
    weather, emails, events, insights = manager.get_all_data()
    
    print(f"\n📊 Data Summary:")
    print(f"Weather: {weather.temperature}, {weather.condition}")
    print(f"Emails: {len(emails)} processed")
    print(f"Events: {len(events)} today")
    print(f"AI Insight: {insights}")
