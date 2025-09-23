#!/usr/bin/env python3
"""
Pydantic Models for Receipt Content
Comprehensive models for all AI-generated receipt content with structured output
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

# =================== DATA MODELS ===================

class WeatherData(BaseModel):
    """Weather information structure"""
    temperature: str = Field(..., description="Current temperature with unit")
    condition: str = Field(..., description="Weather condition description")
    high: str = Field(..., description="High temperature for the day")
    low: str = Field(..., description="Low temperature for the day")
    humidity: str = Field(..., description="Humidity percentage")
    wind_speed: str = Field(..., description="Wind speed with unit")
    feels_like: str = Field(..., description="Feels like temperature")
    icon: str = Field(..., description="Weather icon/emoji")
    history: str = Field(default="", description="Weather history for the day")
    tomorrow_forecast: str = Field(default="", description="Tomorrow's weather forecast")

class EmailData(BaseModel):
    """Email information structure"""
    sender: str = Field(..., description="Email sender")
    subject: str = Field(..., description="Email subject")
    summary: str = Field(..., description="Email summary")
    priority: str = Field(..., description="Priority level")
    time: str = Field(..., description="Email time")
    thread_id: str = Field(..., description="Email thread ID")
    is_important: bool = Field(..., description="Whether email is important")

class CalendarEvent(BaseModel):
    """Calendar event structure"""
    title: str = Field(..., description="Event title")
    start_time: str = Field(..., description="Event start time")
    end_time: str = Field(..., description="Event end time")
    location: str = Field(..., description="Event location")
    description: str = Field(..., description="Event description")
    is_all_day: bool = Field(..., description="Whether event is all day")
    start_date: str = Field(..., description="Event start date")
    start_datetime: str = Field(..., description="Full datetime for AI context")

class TaskData(BaseModel):
    """Task information structure"""
    title: str = Field(..., description="Task title")
    notes: str = Field(..., description="Task notes")
    due_date: str = Field(..., description="Task due date")
    completed: bool = Field(..., description="Whether task is completed")
    priority: str = Field(..., description="Task priority")
    task_id: str = Field(..., description="Task ID")

# =================== AI OUTPUT MODELS ===================

class ReceiptHeader(BaseModel):
    """AI-generated receipt header content"""
    greeting: str = Field(..., description="Personalized greeting in the target language")
    title: str = Field(..., description="Receipt title/subtitle in the target language")
    date_formatted: str = Field(..., description="Beautifully formatted date in the target language")

class ReceiptSummary(BaseModel):
    """AI-generated main content summary"""
    brief: str = Field(..., description="Main contextual brief analyzing all data")

class TaskSection(BaseModel):
    """AI-generated task section"""
    section_title: str = Field(..., description="Section title in target language")

class ShoppingSection(BaseModel):
    """AI-generated shopping section"""
    section_title: str = Field(..., description="Section title in target language")

class ReceiptFooter(BaseModel):
    """AI-generated receipt footer (single localized sentence)"""
    footer_text: str = Field(
        ..., 
        description="Single localized footer sentence like 'Generated on Sunday 21st at 17:14'"
    )

class CompleteReceiptContent(BaseModel):
    """Complete AI-generated receipt content with all sections"""
    header: ReceiptHeader = Field(..., description="Header section with greeting and date")
    summary: ReceiptSummary = Field(..., description="Main content summary")
    task_section: Optional[TaskSection] = Field(None, description="Task section if tasks exist")
    shopping_section: Optional[ShoppingSection] = Field(None, description="Shopping section if items exist")
    footer: ReceiptFooter = Field(..., description="Footer with localized generation sentence")

# =================== CONTEXT MODELS ===================

class AIContext(BaseModel):
    """Context information for AI generation"""
    user_name: str = Field(..., description="User's name")
    language: str = Field(..., description="Target language for generation")
    timezone: str = Field(..., description="User's timezone")
    current_time: datetime = Field(..., description="Current datetime")
    
    # Data context
    weather: Optional[WeatherData] = Field(None, description="Weather data")
    emails: List[EmailData] = Field(default=[], description="Email data")
    events: List[CalendarEvent] = Field(default=[], description="Calendar events")
    tasks: List[TaskData] = Field(default=[], description="Task data")
    shopping_items: List[TaskData] = Field(default=[], description="Shopping items")
    
    # Behavioral context
    time_of_day: str = Field(..., description="Time period (morning, afternoon, evening, night)")
    is_weekend: bool = Field(..., description="Whether it's weekend")
    
class GenerationRequest(BaseModel):
    """Request for AI generation"""
    context: AIContext = Field(..., description="Context for generation")
    instructions: Optional[str] = Field(None, description="Additional instructions")
    max_tokens: int = Field(default=800, description="Maximum tokens for response")

# =================== PRINTER MODELS ===================

class PrintableTask(BaseModel):
    """Task formatted for printing"""
    display_text: str = Field(..., description="Text to display on receipt")
    is_truncated: bool = Field(..., description="Whether text was truncated")
    original_title: str = Field(..., description="Original task title")

class PrintableShoppingItem(BaseModel):
    """Shopping item formatted for printing"""
    display_text: str = Field(..., description="Text to display on receipt")
    is_truncated: bool = Field(..., description="Whether text was truncated")
    original_title: str = Field(..., description="Original item title")

class PrintableContent(BaseModel):
    """Content formatted for printing"""
    receipt_content: CompleteReceiptContent = Field(..., description="AI-generated content")
    printable_tasks: List[PrintableTask] = Field(default=[], description="Tasks formatted for printing")
    printable_shopping: List[PrintableShoppingItem] = Field(default=[], description="Shopping items formatted for printing")
    
    # Layout settings
    paper_width_chars: int = Field(default=32, description="Paper width in characters")
    max_task_length: int = Field(default=70, description="Maximum task title length")
    truncate_indicator: str = Field(default="...", description="Truncation indicator")

# =================== ERROR MODELS ===================

class GenerationError(BaseModel):
    """Error during AI generation"""
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    fallback_content: Optional[str] = Field(None, description="Fallback content if available")

class ValidationError(BaseModel):
    """Validation error for generated content"""
    field: str = Field(..., description="Field that failed validation")
    error: str = Field(..., description="Validation error message")
    received_value: str = Field(..., description="Value that failed validation")

# =================== LEGACY COMPATIBILITY ===================

# For backward compatibility with existing code
MorningBriefResponse = CompleteReceiptContent

class LegacyBriefResponse(BaseModel):
    """Legacy response format for backward compatibility"""
    brief: str = Field(..., description="Main brief content")
    
    @classmethod
    def from_complete_content(cls, content: CompleteReceiptContent) -> "LegacyBriefResponse":
        """Convert from new format to legacy format"""
        return cls(brief=content.summary.brief)
