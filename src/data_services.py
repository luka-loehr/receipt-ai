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
    history: str = ""  # Weather history for the day

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
        
        # Create weather history summary
        weather_history = f"Min: {round(daily['temp']['min'])}°C, Max: {round(daily['temp']['max'])}°C"
        
        return WeatherData(
            temperature=f"{round(current['temp'])}°C",
            condition=current['weather'][0]['description'].title(),
            high=f"{round(daily['temp']['max'])}°C",
            low=f"{round(daily['temp']['min'])}°C",
            humidity=f"{current['humidity']}%",
            wind_speed=f"{round(current['wind_speed'] * 3.6, 1)} km/h",  # Convert m/s to km/h
            feels_like=f"{round(current['feels_like'])}°C",
            icon=icon_emoji,
            history=weather_history
        )

class EmailService:
    """Handles Gmail data fetching and processing"""
    
    def __init__(self):
        # Credentials filename is auto-detected during OAuth; not needed here
        self.max_emails = int(os.getenv('MAX_EMAILS_TO_PROCESS', '10'))
        # Keyword-based filtering removed; AI will infer importance/spam
        
        # Check if unified token exists
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("⚠️  Warning: No Google unified token found. Using mock data.")
    
    def get_recent_emails(self) -> List[EmailData]:
        """Get recent emails - requires Google unified token"""
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("❌ No unified Google token found. Run setup.py to authorize.")
            return []
        
        # Real Gmail API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ No valid unified Google token found. Run setup.py to authorize.")
                return []
        
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
            
            # Neutral defaults; AI handles importance
            subject_lower = subject.lower()
            priority = "medium"
            is_important = False
            
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
        # Credentials filename is auto-detected during OAuth; not needed here
        self.timezone = os.getenv('USER_TIMEZONE', 'Europe/Berlin')
        
        # Check if unified token exists
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("⚠️  Warning: No Google unified token found. Using mock data.")
    
    def get_upcoming_events(self) -> List[CalendarEvent]:
        """Get next 3 calendar events (today, tomorrow, day after) - requires Google unified token"""
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("❌ No unified Google token found. Run setup.py to authorize.")
            return []
        
        # Real Google Calendar API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta
        import pytz
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ No valid unified Google token found. Run setup.py to authorize.")
                return []
        
        # Build Calendar service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get events from start of today to 3 days from now
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        now = today_start.isoformat() + 'Z'  # Start from beginning of today
        end = (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   📅 Found {len(events)} events")
        
        calendar_data = []
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # German month and day names
            german_months = {
                1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
                7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
            }
            german_days = {
                0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 
                4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
            }
            
            if 'dateTime' in event['start']:
                # Time-specific event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                start_time = start_dt.strftime("%H:%M")
                end_time = end_dt.strftime("%H:%M")
                start_date = start_dt.strftime("%Y-%m-%d")
                
                # Create German datetime string
                day_name = german_days[start_dt.weekday()]
                month_name = german_months[start_dt.month]
                start_datetime = f"{day_name}, {start_dt.day}. {month_name} {start_dt.year} um {start_time}"
                is_all_day = False
            else:
                # All-day event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_time = "Ganztägig"
                end_time = ""
                start_date = start_dt.strftime("%Y-%m-%d")
                
                # Create German datetime string
                day_name = german_days[start_dt.weekday()]
                month_name = german_months[start_dt.month]
                start_datetime = f"{day_name}, {start_dt.day}. {month_name} {start_dt.year} (ganztägig)"
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
        

        return calendar_data

class AIService:
    """Handles AI-powered analysis and summarization using OpenAI GPT-4.1 with structured output"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise Exception("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        print("✅ OpenAI AI service initialized successfully")
    
    def generate_morning_brief(self, weather: WeatherData, emails: List[EmailData], events: List[CalendarEvent], tasks: List[TaskData], shopping_list: List[TaskData] = None, user_name: str = "Luka") -> MorningBriefResponse:
        """Generate both greeting and comprehensive brief in a single API call with structured output"""
        
        # Prepare detailed data for AI analysis
        email_summaries = []
        important_emails = []
        for email in emails:
            email_summaries.append(f"Von: {email.sender}, Betreff: {email.subject}")
            if email.is_important:
                important_emails.append(f"WICHTIG: {email.sender} - {email.subject}")
        
        # Get current date and time for context
        current_time = datetime.datetime.now()
        
        # German month and day names
        german_months = {
            1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
            7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }
        german_days = {
            0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 
            4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
        }
        
        # Create German date strings
        day_name = german_days[current_time.weekday()]
        month_name = german_months[current_time.month]
        today_str = f"{day_name}, {current_time.day}. {month_name} {current_time.year}"
        time_str = current_time.strftime("%H:%M")
        day_of_week = day_name  # Use German day name
        
        # Prepare event summaries with better formatting
        event_summaries = []
        all_today_events = []  # All events for today (including past ones)
        upcoming_events = []
        for event in events:
            event_summary = f"{event.title} - {event.start_datetime}"
            event_summaries.append(event_summary)
            if event.start_date == current_time.strftime("%Y-%m-%d"):
                all_today_events.append(event_summary)
            else:
                upcoming_events.append(event_summary)
        
        # Prepare task summaries with priorities and due dates
        task_summaries = []
        high_priority_tasks = []
        overdue_tasks = []
        for task in tasks:
            priority_text = f"[{task.priority.upper()}]" if task.priority != "medium" else ""
            due_info = f" (fällig: {task.due_date})" if task.due_date else ""
            task_summary = f"{priority_text} {task.title}{due_info}".strip()
            task_summaries.append(task_summary)
            
            if task.priority == "high":
                high_priority_tasks.append(task_summary)
            
            # Check for overdue tasks
            if task.due_date:
                try:
                    due_dt = datetime.datetime.strptime(task.due_date, "%Y-%m-%d")
                    if due_dt < current_time:
                        overdue_tasks.append(task_summary)
                except:
                    pass
        
        # Get shopping list items
        shopping_items = [item.title for item in shopping_list] if shopping_list else []
        
        # Build final refined casual prompt
        prompt = f"""
Du bist mein persönlicher Assistent und gibst mir einen kurzen, lockeren Tagesüberblick für {day_of_week}, {time_str}. Schreib so, wie ein Freund oder Klassenkamerad es tun würde: direkt, ehrlich, entspannt – nicht übertrieben cool, aber auf Augenhöhe.

KONTEXT
Aktuelles Wetter: {weather.temperature}, {weather.condition}
Wetterverlauf heute: {weather.history}
Zeit: {time_str} Uhr

E-Mails ({len(emails)}):
{chr(10).join(email_summaries[:5])}
{chr(10).join(important_emails) if important_emails else ""}

Alle heutigen Termine (inkl. bereits vergangener):
{chr(10).join(all_today_events) if all_today_events else "Keine Termine heute"}

Kommende Termine:
{chr(10).join(upcoming_events) if upcoming_events else "Keine kommenden Termine"}

Alle Aufgaben ({len(tasks)}):
{chr(10).join(task_summaries)}
{chr(10).join(overdue_tasks) if overdue_tasks else ""}
{chr(10).join(high_priority_tasks) if high_priority_tasks else ""}

Alle Einkäufe ({len(shopping_items)}):
{chr(10).join(shopping_items) if shopping_items else "Keine Einkäufe geplant"}

ZEITLOGIK:
– Vor 12:00 Uhr: Fokus auf Tagesplanung, anstehende Dinge, was zuerst erledigt werden muss.
– 12:00–17:59 Uhr: Fokus auf das, was noch offen ist und erledigt werden sollte.
– 18:00–19:59 Uhr: Kurzer Rückblick auf den Tag, Restaufgaben, evtl. Vorbereitung auf morgen.
– Ab 20:00 Uhr: Kein Tagesplan mehr! Kein „mach noch schnell…", kein Wetter-Tipp, keine Aktivität mehr draußen. Nur:
  – Was du heute noch digital oder ganz easy machen könntest (z. B. E-Mail, Wecker stellen)
  – Was morgen früh direkt ansteht
  – Ehrlicher Rückblick auf den Tag (inkl. Termine, Wetter, Aufgabenstatus)

RECEIPT PRINTER AGENT:
Du bist ein intelligenter Kassenzettel-Drucker! Der User bekommt alle Aufgaben und Einkäufe sowieso auf seinem physischen Zettel ausgedruckt. Du musst NICHT alle Aufgaben/Einkäufe aufzählen – das macht der Drucker. Stattdessen:
– Highlight nur die 1-3 WICHTIGSTEN Aufgaben/Einkäufe, die wirklich Aufmerksamkeit brauchen
– Mach kurze Kommentare zu den wichtigsten Sachen (warum wichtig, wann zu erledigen, etc.)
– Ignoriere unwichtige/routine Sachen komplett
– Du bist der "Smart Filter" – der User sieht alles, aber du zeigst ihm, was wirklich zählt
– SPRICHE AUF DIE ANZAHL AN: Bei vielen Einkäufen sag sowas wie "du solltest noch X Sachen kaufen" oder "da stehen noch X Einkäufe an"
– Bei vielen Aufgaben: "mach die mal schnell" oder "fang mal an" oder "da warten noch X Aufgaben auf dich"
– Aber NIEMALS die konkreten Details nennen – nur die Anzahl erwähnen

STIL:
– Locker, direkt, in „du"-Form – wie unter Jugendlichen
– Kein Business-Stil, kein Förmlichkeits-Gelaber
– Keine Listen, keine Formatierung, keine künstliche Struktur
– Schreib wie ein echter Mensch: kurze klare Sätze, realistisch und alltagsnah
– Nichts erfinden: Wenn's geregnet hat, sag das. Wenn nichts anstand, dann kurz halten.
– Keine Floskeln wie „einfach mal entspannen" oder „Zeit zum Runterkommen", außer es ergibt sich natürlich.

AUSGABE:
Gib **nur den fertigen Text** als Fließtext zurück. Keine Überschrift, kein Markdown, kein Rahmen, keine Meta-Infos. Einfach losschreiben.
"""
        
        completion = self.client.chat.completions.parse(
            model="gpt-4.1",
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
        
        # Check if unified token exists
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("⚠️  Warning: No Google unified token found. Using mock data.")
    
    def get_tasks(self) -> List[TaskData]:
        """Get recent tasks - requires Google unified token"""
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("❌ No unified Google token found. Run setup.py to authorize.")
            return []
        
        # Real Google Tasks API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ No valid unified Google token found. Run setup.py to authorize.")
                return []
        
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
            
            
            # Process all tasks first
            for task in tasks:
                # Skip completed tasks
                if task.get('status') == 'completed':
                    continue
                
                # Parse due date if available
                due_date = ""
                due_datetime = None
                if 'due' in task:
                    try:
                        due_dt = datetime.datetime.fromisoformat(task['due'].replace('Z', '+00:00'))
                        due_date = due_dt.strftime("%Y-%m-%d")
                        due_datetime = due_dt
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
            
            # Sort tasks by priority: due tasks first (overdue, then due soon), then no due date
            def task_sort_key(task):
                if task.due_date:
                    try:
                        due_dt = datetime.datetime.strptime(task.due_date, "%Y-%m-%d")
                        now = datetime.datetime.now()
                        days_until_due = (due_dt - now).days
                        
                        # Overdue tasks get highest priority (negative numbers sort first)
                        if days_until_due < 0:
                            return (0, days_until_due)  # Overdue: sort by how overdue
                        # Due soon (within 7 days) get medium priority
                        elif days_until_due <= 7:
                            return (1, days_until_due)  # Due soon: sort by days until due
                        # Future tasks get lower priority
                        else:
                            return (2, days_until_due)  # Future: sort by days until due
                    except:
                        return (3, 0)  # Invalid due date: lowest priority
                else:
                    return (3, 0)  # No due date: lowest priority
            
            # Sort tasks by priority
            task_data.sort(key=task_sort_key)
            

            
            return task_data
            
        except Exception as e:
            print(f"⚠️  Error fetching tasks: {e}")
            # Return empty list if there's an error
            return []
    
    def get_tasks_from_list(self, list_name: str) -> List[TaskData]:
        """Get tasks from a specific task list by name"""
        if not os.path.exists('token_autogenerated/unified_google_token.json'):
            print("❌ No unified Google token found. Run setup.py to authorize.")
            return []
        
        # Real Google Tasks API integration
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                return []
        
        # Build Tasks service
        service = build('tasks', 'v1', credentials=creds)
        
        try:
            # Get all task lists
            task_lists = service.tasklists().list().execute()
            target_list = None
            
            # Find the task list by name
            for task_list in task_lists.get('items', []):
                if task_list.get('title', '').lower() == list_name.lower():
                    target_list = task_list
                    break
            
            if not target_list:
                # List not found - print available lists for debugging
                available_lists = [tl.get('title', 'Untitled') for tl in task_lists.get('items', [])]
                print(f"   ⚠️  List '{list_name}' not found. Available lists: {available_lists}")
                return []
            
            list_id = target_list.get('id')
            
            # Get tasks from the specific list
            tasks_result = service.tasks().list(
                tasklist=list_id,
                maxResults=self.max_tasks,
                showCompleted=False,  # Only show incomplete tasks
                showHidden=False
            ).execute()
            
            tasks = tasks_result.get('items', [])
            task_data = []
            
            # Process tasks (same logic as get_tasks)
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
            print(f"⚠️  Error fetching tasks from list '{list_name}': {e}")
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
        print("📊 Fetching data...")
        weather = self.weather_service.get_current_weather()
        emails = self.email_service.get_recent_emails()
        events = self.calendar_service.get_upcoming_events()
        tasks = self.task_service.get_tasks()
        shopping_list = self.task_service.get_tasks_from_list(self.config.shopping_list_name)
        print(f"   🛒 Found {len(shopping_list)} shopping items")
        
        print("🤖 Generating AI brief...")
        brief_response = self.ai_service.generate_morning_brief(weather, emails, events, tasks, shopping_list, user_name)
        
        # Store shopping list for use in daily brief generation
        self.shopping_list = shopping_list
        
        return brief_response
    
    def get_morning_brief(self, user_name: str = "Luka") -> MorningBriefResponse:
        """Alias for get_daily_brief for backward compatibility"""
        return self.get_daily_brief(user_name)

if __name__ == "__main__":
    # Test the data services
    manager = DataManager()
    brief_response = manager.get_morning_brief()
    
    print(f"\n🤖 AI Brief:")
    print(brief_response.brief)
