#!/usr/bin/env python3
"""
Enhanced AI Service Module
Generates ALL receipt content including headers, dates, greetings in any language using structured output
"""

import os
import datetime
import json
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

        return f"""ROLE
You generate daily receipt-style briefs as a JSON object for {context.user_name}. Output MUST be valid JSON matching the schema below—no extra fields or text.

[ASCII ONLY]
- Use only plain ASCII: no emojis, no accented letters (e.g., ü, é, ñ), no degree symbol, no special symbols. Write temperatures as "13 C".

[STYLE]
- Tone: warm, helpful, a little more detailed and narrative. Address {context.user_name} directly.
- Write in {context.language} with {context.timezone} for time, and dates/phrasing in {context.language} style.
- Synthesize information—connect weather, tasks, and upcoming calendar events.
- In `summary.brief`, write a longer, flowing paragraph: up to 6 full sentences. Focus on tasks, upcoming events, and weather.
  - In the **morning**, describe what the weather will be like today and how it might affect plans.
  - In the **evening or night**, mention how the weather was today and what is expected for tomorrow.
  - Mention upcoming calendar events (within 2 days) with detail, not just numbers.
  - For tasks, discuss what's most important or urgent, integrating naturally into the narrative.
  - Explicitly acknowledge task workload: if there are many tasks (e.g., lots of homework) or overdue/high-priority items, say so plainly.
  - Avoid robotic or repetitive lists.
  - Mention counts/numbers naturally. Briefly acknowledge inbox activity (e.g., number of new emails and, if helpful, 1–2 subjects) woven into the narrative.

[TIME-OF-DAY LOGIC]
- Use `context.time_of_day`:
  - "morning": priorities and plans for today, expected weather, and events
  - "afternoon": progress made, what remains, tasks/events, and current weather
  - "evening"/"night": summary of day, how weather was, events completed, outlook for tomorrow

[RESPONSE LENGTH HINTS]
- greeting: ≤7 words
- title: ≤10 words
- summary.brief: up to 6 sentences

[RESPONSE SCHEMA]
Return only:
{{
  "header": {{
    "greeting": "",
    "title": "",
    "date_formatted": ""
  }},
  "summary": {{
    "brief": ""
  }},
  "task_section": {{
    "section_title": ""
  }},
  "shopping_section": {{
    "section_title": ""
  }},
  "footer": {{
    "footer_text": ""
  }}
}}

If context data is missing, use "" for strings or [] for arrays."""

    def _create_user_prompt(self, context: AIContext) -> str:
        """Create detailed user prompt with all context data"""

        # Get language name for AI prompts - just use the string directly
        language_name = context.language

        final_prompt = f"""Generate a personalized daily briefing for {context.user_name} in {language_name}, using the context below.

--- TIME CONTEXT ---
Current time: {context.current_time.strftime('%H:%M')} ({context.timezone})
Day: {context.current_time.strftime('%A')}
Date: {context.current_time.strftime('%Y-%m-%d')}
Time period: {context.time_of_day}
Weekend: {context.is_weekend}

--- WEATHER DATA ---
- Current: {context.weather.temperature}, {context.weather.condition}
- Today's range: {context.weather.low} to {context.weather.high}
- Feels like: {context.weather.feels_like}
- Humidity: {context.weather.humidity}
- Wind: {context.weather.wind_speed}
- History: {context.weather.history}
- Tomorrow forecast: {context.weather.tomorrow_forecast}

--- EMAIL OVERVIEW (10 latest) ---
"""
        for email in context.emails[:10]:
            final_prompt += f"- From: {email.sender} | Subject: {email.subject} | Time: {email.time}\n"

        final_prompt += f"""
--- CALENDAR EVENTS ({len(context.events)} total) ---
"""
        today_events = [e for e in context.events if e.start_date == context.current_time.strftime('%Y-%m-%d')]
        upcoming_events = [e for e in context.events if e.start_date > context.current_time.strftime('%Y-%m-%d')]

        if today_events:
            final_prompt += f"Today's events ({len(today_events)}):\n"
            for event in today_events:
                final_prompt += f"- {event.title} at {event.start_time} | {event.location}\n"

        if upcoming_events:
            final_prompt += f"Upcoming events ({len(upcoming_events)}):\n"
            for event in upcoming_events[:3]:  # Next 3 events
                final_prompt += f"- {event.title} on {event.start_date} at {event.start_time}\n"

        # Format tasks info
        final_prompt += f"""
--- TASKS OVERVIEW ({len(context.tasks)} total) ---
"""
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
                final_prompt += f"OVERDUE ({len(overdue)}): {', '.join([t.title[:30] for t in overdue[:3]])}\n"
            if due_soon:
                final_prompt += f"DUE SOON ({len(due_soon)}): {', '.join([t.title[:30] for t in due_soon[:3]])}\n"
            if high_priority:
                final_prompt += f"HIGH PRIORITY ({len(high_priority)}): {', '.join([t.title[:30] for t in high_priority[:3]])}\n"

        final_prompt += f"""
--- SHOPPING LIST ({len(context.shopping_items)} items) ---
Items: {', '.join([item.title[:20] for item in context.shopping_items[:8]])}

GENERATION REQUIREMENTS:
- Write a detailed summary.brief, up to 6 sentences, connecting weather, tasks, calendar events, and briefly acknowledging inbox activity (mention the number of new emails and optionally 1–2 subject highlights if useful).
- Morning: Focus on today's weather and plans.
- Evening/night: Reflect on today's weather, completed tasks, and mention tomorrow's forecast/events.
- Always use only the fields in the schema.
- No emojis, no degree sign, no special symbols, ASCII only.
- If any data is missing, use "" for strings, [] for arrays.

TASK MENTIONING:
- If there is notable task load (e.g., much homework, many tasks, or multiple overdue/high-priority items), explicitly mention that in the summary.brief in natural language.
- You do not need to list tasks—just reflect the workload level and urgency in 1 short sentence.

⚠️ Output must be valid JSON, matching the schema exactly."""

        return final_prompt

    def rewrite_list_items(self, items: List[str], target_language: str) -> List[str]:
        """Rewrite/translate list items into target_language with corrected grammar and concise phrasing.

        Returns a list of rewritten items in the same order. Falls back to original items on error.
        """
        if not items:
            return []

        # In mock mode, just return originals
        if self.mock_mode or not getattr(self, 'client', None):
            return items

        system_prompt = (
            f"You are a helpful assistant that rewrites short list items in {target_language}. "
            "For each input item: fix grammar, translate to the target language, keep it concise (≤ 12 words), "
            "preserve meaning, remove emojis. Return ONLY a JSON array of strings, one per input item, same order."
        )

        user_payload = {
            "target_language": target_language,
            "items": items,
        }

        try:
            completion = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.2,
                max_tokens=256,
            )

            content = completion.choices[0].message.content.strip()
            # Expect pure JSON array; tolerate code fences
            if content.startswith("```"):
                content = content.strip("`\n ")
                # Remove optional language tag line
                if "\n" in content:
                    content = content.split("\n", 1)[1]

            rewritten = json.loads(content)
            if isinstance(rewritten, list) and all(isinstance(x, str) for x in rewritten):
                # Ensure length matches, otherwise fallback per-item when possible
                if len(rewritten) == len(items):
                    return rewritten
        except Exception:
            pass

        return items
    
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
                return message.parsed
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
            ),
            summary=ReceiptSummary(
                brief=f"Your daily overview is ready. {len(emails)} emails, {len(events)} events, {len(tasks)} tasks."
            ),
            task_section=TaskSection(
                section_title="Tasks"
            ) if tasks else None,
            shopping_section=ShoppingSection(
                section_title="Shopping"
            ) if shopping_items else None,
            footer=ReceiptFooter(
                footer_text=f"Generated on {context.current_time.strftime('%A %d at %H:%M')}"
            ),
        )

def create_ai_service(config: AppConfig) -> EnhancedAIService:
    """Factory function to create AI service"""
    return EnhancedAIService(config)
