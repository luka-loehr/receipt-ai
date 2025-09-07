#!/usr/bin/env python3
"""
Services Module
Modular data services for the receipt printer system
"""

from .weather_service import WeatherService, create_weather_service
from .email_service import EmailService, create_email_service  
from .calendar_service import CalendarService, create_calendar_service
from .task_service import TaskService, create_task_service

__all__ = [
    'WeatherService', 'create_weather_service',
    'EmailService', 'create_email_service', 
    'CalendarService', 'create_calendar_service',
    'TaskService', 'create_task_service'
]
