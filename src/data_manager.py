#!/usr/bin/env python3
"""
Modular Data Manager
Orchestrates all data services and AI generation for the receipt printer system
"""

from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from .config import AppConfig, get_config
from .models import (
    CompleteReceiptContent, WeatherData, EmailData, CalendarEvent, TaskData,
    PrintableContent, PrintableTask, PrintableShoppingItem, LegacyBriefResponse
)
from .ai_service import EnhancedAIService, create_ai_service
from .services import (
    WeatherService, create_weather_service,
    EmailService, create_email_service,
    CalendarService, create_calendar_service,
    TaskService, create_task_service
)


class ModularDataManager:
    """Main data manager that coordinates all services using modular architecture"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or get_config()
        
        # Initialize all services
        self.weather_service = create_weather_service(self.config)
        self.email_service = create_email_service(self.config)
        self.calendar_service = create_calendar_service(self.config)
        self.task_service = create_task_service(self.config)
        self.ai_service = create_ai_service(self.config)
        
        # Storage for cached data
        self.last_shopping_list: List[TaskData] = []
    
    def fetch_all_data(self) -> tuple[Optional[WeatherData], List[EmailData], List[CalendarEvent], List[TaskData], List[TaskData]]:
        """Fetch data from all services concurrently for better performance"""
        print("📊 Fetching data from all services...")
        start_time = time.time()
        
        # Initialize result containers
        weather = None
        emails = []
        events = []
        tasks = []
        shopping_list = []
        
        # Define service functions for concurrent execution
        def fetch_weather():
            try:
                result = self.weather_service.get_current_weather()
                print(f"   🌤️  Weather: {result.temperature}, {result.condition}")
                return ('weather', result)
            except Exception as e:
                print(f"   ⚠️  Weather fetch error: {e}")
                return ('weather', None)
        
        def fetch_emails():
            try:
                result = self.email_service.get_recent_emails()
                return ('emails', result)
            except Exception as e:
                print(f"   ⚠️  Email fetch error: {e}")
                return ('emails', [])
        
        def fetch_events():
            try:
                result = self.calendar_service.get_upcoming_events()
                return ('events', result)
            except Exception as e:
                print(f"   ⚠️  Calendar fetch error: {e}")
                return ('events', [])
        
        def fetch_tasks():
            try:
                result = self.task_service.get_tasks()
                print(f"   ✅ Found {len(result)} tasks")
                return ('tasks', result)
            except Exception as e:
                print(f"   ⚠️  Task fetch error: {e}")
                return ('tasks', [])
        
        def fetch_shopping():
            try:
                result = self.task_service.get_shopping_list()
                self.last_shopping_list = result  # Cache for later use
                print(f"   🛒 Found {len(result)} shopping items")
                return ('shopping', result)
            except Exception as e:
                print(f"   ⚠️  Shopping list fetch error: {e}")
                return ('shopping', [])
        
        # Execute all services concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_service = {
                executor.submit(fetch_weather): 'weather',
                executor.submit(fetch_emails): 'emails', 
                executor.submit(fetch_events): 'events',
                executor.submit(fetch_tasks): 'tasks',
                executor.submit(fetch_shopping): 'shopping'
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_service):
                service_name, result = future.result()
                
                if service_name == 'weather':
                    weather = result
                elif service_name == 'emails':
                    emails = result
                elif service_name == 'events':
                    events = result
                elif service_name == 'tasks':
                    tasks = result
                elif service_name == 'shopping':
                    shopping_list = result
        
        # Calculate and display timing
        elapsed_time = time.time() - start_time
        print(f"   ⚡ All data fetched in {elapsed_time:.2f} seconds")
        
        return weather, emails, events, tasks, shopping_list
    
    def generate_complete_receipt(self) -> tuple[CompleteReceiptContent, tuple]:
        """Generate complete AI-powered receipt content and return raw data for reuse"""
        # Fetch all data
        weather, emails, events, tasks, shopping_list = self.fetch_all_data()
        
        print("\n🤖 Generating AI-Brief...")
        
        # Generate complete content using AI
        try:
            receipt_content = self.ai_service.generate_complete_receipt(
                weather=weather,
                emails=emails,
                events=events,
                tasks=tasks,
                shopping_items=shopping_list
            )
            
            print(f"\n✅ Generated receipt")
            print(f"   📄 Content: {len(receipt_content.summary.brief)} chars")
            print()
            
            # Return both receipt content and raw data for reuse
            raw_data = (weather, emails, events, tasks, shopping_list)
            return receipt_content, raw_data
            
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            raise
    
    def format_for_printing(self, receipt_content: CompleteReceiptContent, 
                           tasks: List[TaskData] = None, 
                           shopping_items: List[TaskData] = None) -> PrintableContent:
        """Format content for thermal printer with text truncation"""
        
        tasks = tasks or []
        shopping_items = shopping_items or self.last_shopping_list
        
        # Format tasks for printing
        printable_tasks = []
        for task in tasks:
            truncated, is_truncated = self._truncate_text(task.title, self.config.paper_width_mm * 2)  # Rough char estimate
            printable_tasks.append(PrintableTask(
                display_text=truncated,
                is_truncated=is_truncated,
                original_title=task.title
            ))
        
        # Format shopping items for printing
        printable_shopping = []
        for item in shopping_items:
            truncated, is_truncated = self._truncate_text(item.title, self.config.paper_width_mm * 2)
            printable_shopping.append(PrintableShoppingItem(
                display_text=truncated,
                is_truncated=is_truncated,
                original_title=item.title
            ))
        
        return PrintableContent(
            receipt_content=receipt_content,
            printable_tasks=printable_tasks,
            printable_shopping=printable_shopping,
            paper_width_chars=32,  # Standard thermal printer width
            max_task_length=70,
            truncate_indicator="..."
        )
    
    def _truncate_text(self, text: str, max_length: int = 70) -> tuple[str, bool]:
        """Truncate text intelligently at word boundaries"""
        if len(text) <= max_length:
            return text, False
        
        # Find the last complete word that fits
        max_chars = max_length - 3  # Leave room for "..."
        words = text.split()
        truncated_title = ""
        
        for word in words:
            test_title = truncated_title + (" " if truncated_title else "") + word
            if len(test_title) <= max_chars:
                truncated_title = test_title
            else:
                break
        
        if truncated_title:
            return truncated_title + "...", True
        else:
            # If even the first word is too long, force truncate
            return text[:max_chars] + "...", True
    
    def get_daily_brief(self, user_name: Optional[str] = None) -> CompleteReceiptContent:
        """Generate daily brief - main entry point"""
        if user_name and user_name != self.config.user_name:
            # Update config if user name is different
            from .config import set_user_name
            set_user_name(user_name)
        
        return self.generate_complete_receipt()
    
    def get_morning_brief(self, user_name: Optional[str] = None) -> LegacyBriefResponse:
        """Legacy compatibility method"""
        complete_content = self.get_daily_brief(user_name)
        return LegacyBriefResponse.from_complete_content(complete_content)
    
    def get_shopping_list(self) -> List[TaskData]:
        """Get the cached shopping list"""
        return self.last_shopping_list
    
    def set_language(self, language_code: str) -> None:
        """Change the system language and reinitialize AI service"""
        from .config import Language, set_language
        
        try:
            language = Language(language_code.lower())
            set_language(language)
            
            # Reinitialize AI service with new language
            self.ai_service = create_ai_service(self.config)
            
            # Reinitialize other services that depend on language
            self.calendar_service = create_calendar_service(self.config)
            self.task_service = create_task_service(self.config)
            
            print(f"✅ Language changed to: {self.config.get_language_code()}")
            
        except ValueError:
            print(f"❌ Unsupported language: {language_code}")
            raise ValueError(f"Language '{language_code}' is not supported")


# Factory function for backward compatibility
def create_data_manager(config: Optional[AppConfig] = None) -> ModularDataManager:
    """Create a new data manager instance"""
    return ModularDataManager(config)


# Global instance for backward compatibility
_global_manager: Optional[ModularDataManager] = None

def get_data_manager() -> ModularDataManager:
    """Get or create the global data manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = ModularDataManager()
    return _global_manager
