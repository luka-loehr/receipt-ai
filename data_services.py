#!/usr/bin/env python3
"""
Data Services Module
Handles real-time data fetching for weather, emails, calendar, tasks, and AI summarization
"""

import os
import json
import datetime
import pytz
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

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
    icon: str  # Weather icon/emoji

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
    start_date: str  # Full date (e.g., "2025-01-20")
    start_datetime: str  # Full datetime for AI context

@dataclass
class TaskData:
    """Google Task information structure"""
    title: str
    notes: str
    due_date: str
    completed: bool
    priority: str
    task_id: str





# Pydantic models for structured AI output
class MorningBriefResponse(BaseModel):
    """Structured response from AI for morning brief generation"""
    greeting: str  # Time-appropriate greeting (e.g., "Guten Morgen, Luka")
    brief: str     # Main content brief
    # Future fields can be added here:
    # priority_tasks: List[str]
    # motivational_quote: str
    # weather_summary: str

class WeatherService:
    """Handles weather data fetching from OpenWeatherMap One Call API 3.0"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.location = os.getenv('WEATHER_LOCATION', 'Karlsruhe,DE')
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        
        if not self.api_key:
            print("⚠️  Warning: No OpenWeatherMap API key found. Using mock data.")
    
    def _get_weather_icon(self, weather_code: str, is_day: bool = True) -> str:
        """Map OpenWeather weather codes to ASCII-compatible icons"""
        # OpenWeather weather codes mapping to ASCII characters for thermal printer compatibility
        icon_map = {
            # Clear sky
            "01d": "[SUN]",  # clear sky day
            "01n": "[MOON]",  # clear sky night
            
            # Few clouds
            "02d": "[SUN_CLOUD]",  # few clouds day
            "02n": "[CLOUD]",  # few clouds night
            
            # Scattered clouds
            "03d": "[CLOUD]",  # scattered clouds
            "03n": "[CLOUD]",
            
            # Broken clouds
            "04d": "[CLOUD]",  # broken clouds
            "04n": "[CLOUD]",
            
            # Shower rain
            "09d": "[RAIN]",  # shower rain
            "09n": "[RAIN]",
            
            # Rain
            "10d": "[RAIN]",  # rain day
            "10n": "[RAIN]",  # rain night
            
            # Thunderstorm
            "11d": "[STORM]",  # thunderstorm
            "11n": "[STORM]",
            
            # Snow
            "13d": "[SNOW]",  # snow
            "13n": "[SNOW]",
            
            # Mist
            "50d": "[FOG]",  # mist
            "50n": "[FOG]",
        }
        
        return icon_map.get(weather_code, "[WEATHER]")  # Default icon
    
    def _get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates for the location using Geocoding API"""
        geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': self.location,
            'appid': self.api_key,
            'limit': 1
        }
        
        response = requests.get(geocoding_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise Exception(f"Location '{self.location}' not found")
        
        return data[0]['lat'], data[0]['lon']
    
    def get_current_weather(self) -> WeatherData:
        """Get current weather data using One Call API 3.0 - requires API key"""
        if not self.api_key:
            raise Exception("OpenWeatherMap API key required")
        
        # Get coordinates for the location
        lat, lon = self._get_coordinates()
        
        # Use One Call API 3.0
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'exclude': 'minutely,alerts'  # Exclude unnecessary data to save API calls
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract current weather
        current = data['current']
        daily = data['daily'][0]  # Today's forecast
        
        # Get weather icon
        weather_icon = current['weather'][0]['icon']
        icon_emoji = self._get_weather_icon(weather_icon)
        
        return WeatherData(
            temperature=f"{round(current['temp'])}°C",
            condition=current['weather'][0]['description'].title(),
            high=f"{round(daily['temp']['max'])}°C",
            low=f"{round(daily['temp']['min'])}°C",
            humidity=f"{current['humidity']}%",
            wind_speed=f"{round(current['wind_speed'] * 3.6, 1)} km/h",  # Convert m/s to km/h
            feels_like=f"{round(current['feels_like'])}°C",
            icon=icon_emoji
        )

class EmailService:
    """Handles Gmail data fetching and processing"""
    
    def __init__(self):
        # Use the unified Google credentials file
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'cloud_credentials/google_credentials.json')
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
        if os.path.exists('tokens_autogenerated/gmail_token.json'):
            creds = Credentials.from_authorized_user_file('tokens_autogenerated/gmail_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('tokens_autogenerated/gmail_token.json', 'w') as token:
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
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'cloud_credentials/google_credentials.json')
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
        if os.path.exists('tokens_autogenerated/calendar_token.json'):
            creds = Credentials.from_authorized_user_file('tokens_autogenerated/calendar_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('tokens_autogenerated/calendar_token.json', 'w') as token:
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
                start_date = start_dt.strftime("%Y-%m-%d")
                start_datetime = start_dt.strftime("%A, %d. %B %Y um %H:%M")
                is_all_day = False
            else:
                # All-day event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_time = "Ganztägig"
                end_time = ""
                start_date = start_dt.strftime("%Y-%m-%d")
                start_datetime = start_dt.strftime("%A, %d. %B %Y (ganztägig)")
                is_all_day = True
            
            calendar_data.append(CalendarEvent(
                title=event['summary'],
                start_time=start_time,
                end_time=end_time,
                location=event.get('location', ''),
                description=event.get('description', ''),
                is_all_day=is_all_day,
                start_date=start_date,
                start_datetime=start_datetime
            ))
        
        print(f"   📅 Returning {len(calendar_data)} processed events")
        return calendar_data

class AIService:
    """Handles AI-powered analysis and summarization using OpenAI GPT-4o with structured output"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise Exception("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        print("✅ OpenAI AI service initialized successfully")
    
    def generate_morning_brief(self, weather: WeatherData, emails: List[EmailData], events: List[CalendarEvent], tasks: List[TaskData], user_name: str = "Luka") -> MorningBriefResponse:
        """Generate both greeting and comprehensive brief in a single API call with structured output"""
        
        # Prepare data for AI analysis
        email_summaries = []
        for email in emails:
            email_summaries.append(f"Von: {email.sender}, Betreff: {email.subject}")
        
        # Get current date and time for context
        current_time = datetime.datetime.now()
        today_str = current_time.strftime("%A, %d. %B %Y")
        time_str = current_time.strftime("%H:%M")
        day_of_week = current_time.strftime("%A")  # Monday, Tuesday, etc.
        
        event_summaries = []
        for event in events:
            event_summaries.append(f"{event.title} - {event.start_datetime}")
        
        task_summaries = []
        for task in tasks:
            priority_text = f"[{task.priority.upper()}]" if task.priority != "medium" else ""
            task_summaries.append(f"{priority_text} {task.title}".strip())
        

        
        prompt = f"""Deutscher Tagesüberblick für {user_name} - {day_of_week}, {time_str}

Wetter: Jetzt {weather.temperature}°C, heute {weather.low}-{weather.high}°C, {weather.condition}
E-Mails: {len(emails)} total
Termine: {chr(10).join(event_summaries)}
Aufgaben: {len(tasks)} total

Erstelle:
- Begrüßung: max 4 Wörter
- Brief: ca. 80 Wörter, erwähne Wetter + wichtige E-Mails + heutige Termine + Aufgaben

WICHTIG: Verwende KEINE Emojis im Text - nur normale Buchstaben und Satzzeichen."""
        
        completion = self.client.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=MorningBriefResponse
        )
        
        message = completion.choices[0].message
        if message.parsed:
            return message.parsed
        else:
            raise Exception(f"AI refused to generate content: {message.refusal}")





class TaskService:
    """Handles Google Tasks data fetching"""
    
    def __init__(self):
        # Use the unified Google credentials file
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'cloud_credentials/google_credentials.json')
        self.max_tasks = int(os.getenv('MAX_TASKS_TO_PROCESS', '10'))
        
        if not os.path.exists(self.credentials_file):
            print("⚠️  Warning: No Google credentials found. Using mock data.")
    
    def get_tasks(self) -> List[TaskData]:
        """Get recent tasks - requires Google credentials"""
        if not os.path.exists(self.credentials_file):
            raise Exception("Google credentials file required")
        
        # Real Google Tasks API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        
        # Get credentials
        creds = None
        if os.path.exists('tokens_autogenerated/tasks_token.json'):
            creds = Credentials.from_authorized_user_file('tokens_autogenerated/tasks_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('tokens_autogenerated/tasks_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Build Tasks service
        service = build('tasks', 'v1', credentials=creds)
        
        # Get tasks from the default task list
        try:
            # First get the default task list
            task_lists = service.tasklists().list().execute()
            default_list = None
            
            # Find the default task list (usually "@default")
            for task_list in task_lists.get('items', []):
                if task_list.get('id') == '@default':
                    default_list = task_list
                    break
            
            if not default_list:
                # If no @default list, use the first available one
                default_list = task_lists.get('items', [{}])[0]
            
            list_id = default_list.get('id')
            
            # Get tasks from the selected list
            tasks_result = service.tasks().list(
                tasklist=list_id,
                maxResults=self.max_tasks,
                showCompleted=False,  # Only show incomplete tasks
                showHidden=False
            ).execute()
            
            tasks = tasks_result.get('items', [])
            task_data = []
            
            for task in tasks:
                # Skip completed tasks
                if task.get('status') == 'completed':
                    continue
                
                # Parse due date if available
                due_date = ""
                if 'due' in task:
                    try:
                        due_dt = datetime.datetime.fromisoformat(task['due'].replace('Z', '+00:00'))
                        due_date = due_dt.strftime("%Y-%m-%d")
                    except:
                        due_date = task['due']
                
                # Determine priority
                priority = "medium"
                if 'notes' in task and task['notes']:
                    notes_lower = task['notes'].lower()
                    if any(word in notes_lower for word in ['urgent', 'high', 'important']):
                        priority = "high"
                    elif any(word in notes_lower for word in ['low', 'optional']):
                        priority = "low"
                
                task_data.append(TaskData(
                    title=task.get('title', 'Untitled Task'),
                    notes=task.get('notes', ''),
                    due_date=due_date,
                    completed=False,
                    priority=priority,
                    task_id=task.get('id', '')
                ))
            
            return task_data
            
        except Exception as e:
            print(f"⚠️  Error fetching tasks: {e}")
            # Return empty list if there's an error
            return []

class DataManager:
    """Main data manager that coordinates all services"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.task_service = TaskService()

        self.ai_service = AIService()
    
    def get_daily_brief(self, user_name: str = "Luka") -> MorningBriefResponse:
        """Fetch all data and return AI-generated daily brief with greeting in a single API call"""
        print("🌤️  Fetching weather data...")
        weather = self.weather_service.get_current_weather()
        
        print("📧  Fetching email data...")
        emails = self.email_service.get_recent_emails()
        
        print("📅  Fetching calendar data...")
        events = self.calendar_service.get_upcoming_events()
        
        print("✅  Fetching task data...")
        tasks = self.task_service.get_tasks()
        

        
        print("🤖  Generating AI brief and greeting...")
        brief_response = self.ai_service.generate_morning_brief(weather, emails, events, tasks, user_name)
        
        return brief_response
    
    def get_morning_brief(self, user_name: str = "Luka") -> MorningBriefResponse:
        """Alias for get_daily_brief for backward compatibility"""
        return self.get_daily_brief(user_name)

if __name__ == "__main__":
    # Test the data services
    manager = DataManager()
    brief_response = manager.get_morning_brief()
    
    print(f"\n👋 AI Greeting:")
    print(brief_response.greeting)
    print(f"\n🤖 AI Brief:")
    print(brief_response.brief)
