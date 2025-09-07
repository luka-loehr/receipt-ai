#!/usr/bin/env python3
"""
Configuration Module
Centralized configuration for the receipt printer system including language settings
"""

import os
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum

# No need for hardcoded languages! AI can handle any language.
# Just use strings directly - much simpler and more flexible.

class AppConfig(BaseModel):
    """Application configuration"""
    
    # Language Settings
    language: str = Field(default="german", description="System language - AI can handle any language!")
    user_name: str = Field(default="Luka", description="User's name for personalization")
    timezone: str = Field(default="Europe/Berlin", description="User's timezone")
    
    # AI Settings  
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    ai_model: str = Field(default="gpt-4o-mini", description="AI model to use")
    max_tokens: int = Field(default=800, description="Maximum output tokens for AI responses")
    
    # Weather Settings
    openweather_api_key: Optional[str] = Field(default=None, description="OpenWeatherMap API key")
    weather_location: str = Field(default="Karlsruhe,DE", description="Weather location")
    
    # Email Settings
    max_emails_to_process: int = Field(default=10, description="Maximum emails to process")
    email_priority_keywords: list[str] = Field(
        default=["urgent", "important", "asap", "deadline", "meeting"],
        description="Keywords that indicate high priority emails"
    )
    email_spam_filters: list[str] = Field(
        default=["newsletter", "marketing", "promotion", "unsubscribe"],
        description="Keywords to filter out spam emails"
    )
    
    # Task Settings
    max_tasks_to_process: int = Field(default=15, description="Maximum tasks to process")
    general_tasks_list_name: str = Field(default="General", description="Name of general tasks list in Google Tasks")
    shopping_list_name: str = Field(default="Shopping List", description="Name of shopping list in Google Tasks")
    
    # Printer Settings
    thermal_printer_type: str = Field(default="file_test", description="Thermal printer configuration type")
    paper_width_mm: int = Field(default=58, description="Thermal paper width in mm")
    
    # Output Settings
    output_png_file: str = Field(default="outputs/png/daily_brief.png", description="PNG output file path")
    output_txt_file: str = Field(default="outputs/txt/daily_brief.txt", description="TXT output file path")
    output_escpos_file: str = Field(default="outputs/escpos/daily_brief.txt", description="ESC/POS output file path")
    
    @classmethod
    def from_environment(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        # Load .env file if it exists
        from dotenv import load_dotenv
        load_dotenv()
        
        return cls(
            language=os.getenv('RECEIPT_LANGUAGE', 'german').lower(),
            user_name=os.getenv('USER_NAME', 'Luka'),
            timezone=os.getenv('USER_TIMEZONE', 'Europe/Berlin'),
            
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            ai_model=os.getenv('AI_MODEL', 'gpt-4o-mini'),
            max_tokens=int(os.getenv('MAX_OUTPUT_TOKENS', '800')),
            
            openweather_api_key=os.getenv('OPENWEATHER_API_KEY'),
            weather_location=os.getenv('WEATHER_LOCATION', 'Karlsruhe,DE'),
            
            max_emails_to_process=int(os.getenv('MAX_EMAILS_TO_PROCESS', '10')),
            email_priority_keywords=os.getenv('EMAIL_PRIORITY_KEYWORDS', 'urgent,important,asap,deadline,meeting').split(','),
            email_spam_filters=os.getenv('EMAIL_SPAM_FILTERS', 'newsletter,marketing,promotion,unsubscribe').split(','),
            
            max_tasks_to_process=int(os.getenv('MAX_TASKS_TO_PROCESS', '15')),
            general_tasks_list_name=os.getenv('GENERAL_TASKS_LIST_NAME', 'Allgemeines'),
            shopping_list_name=os.getenv('SHOPPING_LIST_NAME', 'Einkaufsliste'),
            
            thermal_printer_type=os.getenv('THERMAL_PRINTER_TYPE', 'file_test'),
            paper_width_mm=int(os.getenv('PAPER_WIDTH_MM', '58')),
            
            output_png_file=os.getenv('OUTPUT_PNG_FILE', 'outputs/png/daily_brief.png'),
            output_txt_file=os.getenv('OUTPUT_TXT_FILE', 'outputs/txt/daily_brief.txt'),
            output_escpos_file=os.getenv('OUTPUT_ESCPOS_FILE', 'outputs/escpos/daily_brief.txt')
        )
    
    def get_language_code(self) -> str:
        """Get language code for AI prompts - AI can handle any language!"""
        # Just return the language name - AI is smart enough to understand any language
        return self.language.title()
    
    def get_shopping_list_name_localized(self) -> str:
        """Get localized shopping list name - AI will handle this dynamically"""
        # AI will generate the appropriate shopping list name in any language
        return self.shopping_list_name

# Global configuration instance - will be loaded dynamically
config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get the current configuration, loading from environment if needed"""
    global config
    if config is None:
        config = AppConfig.from_environment()
    return config

def set_language(language_name: str) -> None:
    """Set the system language - AI can handle ANY language!"""
    global config
    if config is None:
        config = get_config()
    config.language = language_name.lower()

def set_user_name(user_name: str) -> None:
    """Set the user name"""
    global config
    if config is None:
        config = get_config()
    config.user_name = user_name
