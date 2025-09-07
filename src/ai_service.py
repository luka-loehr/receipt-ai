#!/usr/bin/env python3
"""
Enhanced AI Service Module
Generates ALL receipt content including headers, dates, greetings in any language using structured output
"""

import os
import datetime
from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel

from .models import (
    CompleteReceiptContent, ReceiptHeader, ReceiptSummary, TaskSection, 
    ShoppingSection, ReceiptFooter, AIContext, GenerationRequest,
    WeatherData, EmailData, CalendarEvent, TaskData, GenerationError
)
from .config import AppConfig


class EnhancedAIService:
    """AI service that generates complete receipt content with structured output"""
    
    def __init__(self, config: AppConfig, mock_mode: bool = False):
        self.config = config
        self.api_key = config.openai_api_key
        self.mock_mode = mock_mode
        
        # Check if API key is available
        if not self.api_key:
            print("⚠️  Warning: No OpenAI API key found. Using mock mode.")
            self.mock_mode = True
        
        if not self.mock_mode and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print(f"✅ Enhanced AI service initialized successfully with model {config.ai_model}")
            except Exception as e:
                print(f"⚠️  Error initializing OpenAI client: {e}. Using mock mode.")
                self.mock_mode = True
                self.client = None
        else:
            self.client = None
            print("🤖 Enhanced AI service initialized in MOCK MODE")
    
    def _build_context(self, weather: Optional[WeatherData], emails: List[EmailData], 
                      events: List[CalendarEvent], tasks: List[TaskData], 
                      shopping_items: List[TaskData]) -> AIContext:
        """Build comprehensive context for AI generation"""
        
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Check if weekend
        is_weekend = current_time.weekday() >= 5
        
        return AIContext(
            user_name=self.config.user_name,
            language=self.config.get_language_code(),
            timezone=self.config.timezone,
            current_time=current_time,
            weather=weather,
            emails=emails,
            events=events,
            tasks=tasks,
            shopping_items=shopping_items,
            time_of_day=time_of_day,
            is_weekend=is_weekend
        )
    
    def _create_system_prompt(self, context: AIContext) -> str:
        """Create comprehensive system prompt for receipt generation"""
        
        return f"""You are an intelligent receipt generator AI that creates personalized daily briefings. You MUST generate ALL content in {context.language} including headers, dates, greetings, and section titles.

CORE RESPONSIBILITIES:
1. Generate a time-appropriate greeting in {context.language}
2. Format the current date beautifully in {context.language} cultural style
3. Create contextual section titles in {context.language}
4. Analyze all provided data and create meaningful insights
5. Adapt tone and content based on time of day ({context.time_of_day})

LANGUAGE & CULTURAL ADAPTATION:
- Write EVERYTHING in {context.language} (dates, greetings, titles, content)
- Use appropriate cultural date formatting for {context.language}
- Apply cultural communication styles and expressions
- Use time-appropriate greetings for the culture
- Ensure proper formality level for the language

TIME-BASED BEHAVIOR:
- Morning (5-12): Focus on day planning, priorities, motivation for the day ahead
- Afternoon (12-17): Review progress, what still needs attention
- Evening (17-22): Wrap up the day, remaining tasks, tomorrow preparation  
- Night (22-5): Gentle reflection, minimal action items, rest-focused

TONE & STYLE:
- Write like a helpful, intelligent friend
- Be concise but warm and personal
- Use {context.user_name}'s name naturally
- Match the cultural communication style of {context.language}
- Be encouraging and practical

CONTENT STRATEGY:
- Don't list every detail - be a smart filter
- Highlight only the most important/urgent items
- Make contextual connections (weather → activities, time → priorities)
- Provide actionable insights, not just data dumps
- Reference quantities when relevant ("you have X tasks", "X emails waiting")

OUTPUT REQUIREMENTS:
- Generate proper cultural date formatting
- Create appropriate section headers in {context.language}  
- Use natural, flowing language (no bullet points or lists in the main brief)
- Ensure all text fields are filled appropriately
- Adapt greeting based on current time in {context.timezone}"""

    def _create_user_prompt(self, context: AIContext) -> str:
        """Create detailed user prompt with all context data"""
        
        # Format current time info
        time_info = f"""
CURRENT TIME CONTEXT:
- Current time: {context.current_time.strftime('%H:%M')} ({context.timezone})
- Day: {context.current_time.strftime('%A')}
- Date: {context.current_time.strftime('%Y-%m-%d')}
- Time period: {context.time_of_day}
- Weekend: {context.is_weekend}
"""
        
        # Format weather info
        weather_info = ""
        if context.weather:
            weather_info = f"""
WEATHER DATA:
- Current: {context.weather.temperature}, {context.weather.condition}
- Today's range: {context.weather.low} to {context.weather.high}
- Feels like: {context.weather.feels_like}
- Humidity: {context.weather.humidity}
- Wind: {context.weather.wind_speed}
- History: {context.weather.history}
"""
        
        # Format email info
        email_info = f"""
EMAIL OVERVIEW ({len(context.emails)} total):"""
        for i, email in enumerate(context.emails[:5]):  # Top 5 emails
            priority_marker = "⚠️ IMPORTANT" if email.is_important else ""
            email_info += f"""
- From: {email.sender} | Subject: {email.subject} | Time: {email.time} {priority_marker}"""
        
        # Format events info
        events_info = f"""
CALENDAR EVENTS ({len(context.events)} total):"""
        today_events = [e for e in context.events if e.start_date == context.current_time.strftime('%Y-%m-%d')]
        upcoming_events = [e for e in context.events if e.start_date > context.current_time.strftime('%Y-%m-%d')]
        
        if today_events:
            events_info += f"""
Today's events ({len(today_events)}):"""
            for event in today_events:
                events_info += f"""
- {event.title} at {event.start_time} | {event.location}"""
        
        if upcoming_events:
            events_info += f"""
Upcoming events ({len(upcoming_events)}):"""
            for event in upcoming_events[:3]:  # Next 3 events
                events_info += f"""
- {event.title} on {event.start_date} at {event.start_time}"""
        
        # Format tasks info
        tasks_info = f"""
TASKS OVERVIEW ({len(context.tasks)} total):"""
        if context.tasks:
            # Separate by priority and due dates
            high_priority = [t for t in context.tasks if t.priority == "high"]
            overdue = []
            due_soon = []
            
            for task in context.tasks:
                if task.due_date:
                    try:
                        due_dt = datetime.datetime.strptime(task.due_date, "%Y-%m-%d")
                        days_until = (due_dt - context.current_time).days
                        if days_until < 0:
                            overdue.append(task)
                        elif days_until <= 3:
                            due_soon.append(task)
                    except:
                        pass
            
            if overdue:
                tasks_info += f"""
⚠️ OVERDUE ({len(overdue)}): {', '.join([t.title[:30] for t in overdue[:3]])}"""
            if due_soon:
                tasks_info += f"""
🔥 DUE SOON ({len(due_soon)}): {', '.join([t.title[:30] for t in due_soon[:3]])}"""
            if high_priority:
                tasks_info += f"""
❗ HIGH PRIORITY ({len(high_priority)}): {', '.join([t.title[:30] for t in high_priority[:3]])}"""
        
        # Format shopping info
        shopping_info = f"""
SHOPPING LIST ({len(context.shopping_items)} items):"""
        if context.shopping_items:
            shopping_info += f"""
Items: {', '.join([item.title[:20] for item in context.shopping_items[:8]])}"""
        
        # Get language name for AI prompts - just use the string directly
        language_name = context.language
        
        final_prompt = f"""Generate a complete personalized daily briefing for {context.user_name} in {language_name}.

{time_info}
{weather_info}
{email_info}
{events_info}  
{tasks_info}
{shopping_info}

GENERATION REQUIREMENTS:
- Create appropriate greeting for {context.time_of_day} in {language_name}
- Format date in beautiful {language_name} cultural style
- Generate section titles in {language_name}
- Write main brief analyzing the context intelligently
- Focus on what's most important for {context.time_of_day}
- Be culturally appropriate for {language_name}
- Reference quantities naturally ("you have X tasks to tackle")
- Connect related information (weather + activities, time + priorities)

NOTE: You can handle ANY language! If {language_name} is not a common language, generate content in that language using your knowledge of world languages.

Remember: You are creating a smart, personalized daily assistant - not just listing data!"""
        
        return final_prompt
    
    def generate_complete_receipt(self, weather: Optional[WeatherData] = None,
                                emails: List[EmailData] = None,
                                events: List[CalendarEvent] = None,
                                tasks: List[TaskData] = None,
                                shopping_items: List[TaskData] = None) -> CompleteReceiptContent:
        """Generate complete receipt content with structured output"""
        
        # Default empty lists if None
        emails = emails or []
        events = events or []
        tasks = tasks or []
        shopping_items = shopping_items or []
        
        # Build context
        context = self._build_context(weather, emails, events, tasks, shopping_items)
        
        # If in mock mode, return fallback content
        if self.mock_mode:
            print("🤖 Using mock AI content generation")
            return self._create_fallback_content(context, emails, events, tasks, shopping_items)
        
        # Create prompts
        system_prompt = self._create_system_prompt(context)
        user_prompt = self._create_user_prompt(context)
        
        try:
            # Use OpenAI structured output with Pydantic
            completion = self.client.chat.completions.parse(
                model=self.config.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=CompleteReceiptContent,
                max_tokens=self.config.max_tokens,
                temperature=0.7  # Slight creativity for natural language
            )
            
            message = completion.choices[0].message
            if message.parsed:
                # Ensure metadata is populated
                result = message.parsed
                result.total_emails = len(emails)
                result.total_events = len(events) 
                result.total_tasks = len(tasks)
                result.total_shopping_items = len(shopping_items)
                result.language = context.language
                
                return result
            else:
                raise Exception(f"AI refused to generate content: {message.refusal}")
                
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            # Return fallback content
            return self._create_fallback_content(context, emails, events, tasks, shopping_items)
    
    def _create_fallback_content(self, context: AIContext, emails: List[EmailData],
                               events: List[CalendarEvent], tasks: List[TaskData],
                               shopping_items: List[TaskData]) -> CompleteReceiptContent:
        """Create fallback content when AI generation fails"""
        
        # Basic greeting logic
        hour = context.current_time.hour
        # Let AI handle the language - just use English fallback
        if 5 <= hour < 12:
            greeting = f"Good morning, {context.user_name}!"
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {context.user_name}!"
        elif 17 <= hour < 22:
            greeting = f"Good evening, {context.user_name}!"
        else:
            greeting = f"Good night, {context.user_name}!"
        
        title = "Daily Brief"
        date_formatted = context.current_time.strftime("%A, %B %d, %Y")
        
        
        return CompleteReceiptContent(
            header=ReceiptHeader(
                greeting=greeting,
                title=title,
                date_formatted=date_formatted,
                time_formatted=context.current_time.strftime("%H:%M")
            ),
            summary=ReceiptSummary(
                brief=f"Your daily overview is ready. {len(emails)} emails, {len(events)} events, {len(tasks)} tasks.",
                day_outlook="Have a productive day!"
            ),
            task_section=TaskSection(
                section_title="Tasks" if context.language == "english" else "Tasks",
                task_summary=f"{len(tasks)} tasks await your attention.",
                display_count=len(tasks)
            ) if tasks else None,
            shopping_section=ShoppingSection(
                section_title="Shopping" if context.language == "english" else "Shopping",
                shopping_summary=f"{len(shopping_items)} items to buy.",
                display_count=len(shopping_items)
            ) if shopping_items else None,
            footer=ReceiptFooter(
                timestamp_label="Generated at" if context.language == "english" else "Generated at",
                timestamp=context.current_time.strftime("%H:%M"),
                motivational_note="Stay organized!"
            ),
            language=context.language,
            total_emails=len(emails),
            total_events=len(events),
            total_tasks=len(tasks),
            total_shopping_items=len(shopping_items)
        )

def create_ai_service(config: AppConfig) -> EnhancedAIService:
    """Factory function to create AI service"""
    return EnhancedAIService(config)
