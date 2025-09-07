#!/usr/bin/env python3
"""
Language Switcher for Receipt Printer
Easy way to change language and run daily brief
"""

import sys
from src.config import set_language, Language, get_config

def show_languages():
    """Display available languages"""
    print("🌍 Available Languages:")
    print("=" * 40)
    for i, lang in enumerate(Language, 1):
        print(f"{i:2}. {lang.value.title():12} ({lang.value})")
    print("=" * 40)

def select_language():
    """Interactive language selection"""
    show_languages()
    
    while True:
        try:
            choice = input("\nSelect language (1-12) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Goodbye!")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(Language):
                selected_lang = list(Language)[choice_num - 1]
                return selected_lang
            else:
                print(f"❌ Please enter a number between 1 and {len(Language)}")
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")

def run_daily_brief():
    """Run the daily brief with current language"""
    print(f"\n📅 Running daily brief in {get_config().language.value.title()}...")
    
    try:
        from src.daily_brief import main
        main()
    except Exception as e:
        print(f"❌ Error running daily brief: {e}")

def main():
    """Main language switcher"""
    print("🌍 Receipt Printer Language Switcher")
    print("=" * 40)
    
    # Show current language
    current_lang = get_config().language
    print(f"Current language: {current_lang.value.title()}")
    
    # Let user select new language
    new_lang = select_language()
    
    # Set the new language
    set_language(new_lang)
    print(f"✅ Language set to: {new_lang.value.title()}")
    
    # Ask if they want to run daily brief
    try:
        run_brief = input(f"\nRun daily brief in {new_lang.value.title()}? (y/n): ").strip().lower()
    except EOFError:
        # Handle automated testing or non-interactive mode
        run_brief = 'n'
    
    if run_brief in ['y', 'yes', '']:
        run_daily_brief()
    else:
        print(f"✅ Language set to {new_lang.value.title()}. Run 'python3 daily_brief.py' when ready!")

if __name__ == "__main__":
    main()
