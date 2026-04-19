#!/usr/bin/env python3
"""
Preview of the new receipt design
Shows what the actual thermal printer output will look like
"""

from datetime import datetime, timedelta
import random

def preview_receipt():
    now = datetime.now()
    
    # German date formatting
    german_months = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
        7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    german_days = {
        0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 
        4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
    }
    german_days_short = {
        0: 'Mo', 1: 'Di', 2: 'Mi', 3: 'Do', 
        4: 'Fr', 5: 'Sa', 6: 'So'
    }
    
    day_name = german_days[now.weekday()]
    month_name = german_months[now.month]
    date_str = f"{day_name}, {now.day}. {month_name} {now.year}"
    time_str = now.strftime("%H:%M Uhr")
    
    # Calculate week view
    days_since_monday = now.weekday()
    start_of_week = now - timedelta(days=days_since_monday)
    
    print("\n" + "="*40)
    print("NEW RECEIPT DESIGN PREVIEW")
    print("="*40 + "\n")
    
    # Header
    print("╔═══════════════════════════════════╗")
    print("║      ☀️  DAILY BRIEFING  ☀️       ║")
    print("╚═══════════════════════════════════╝")
    print()
    print("      Guten Abend, Luka!")
    print()
    
    # Date & Time Block
    print("┌─────────────────────────────────┐")
    print(f"│ {date_str:^31} │")
    print(f"│ {time_str:^31} │")
    print("└─────────────────────────────────┘")
    print()
    
    # Mini Calendar - Week View
    print("📅 WOCHENÜBERSICHT")
    print("─────────────────────────────────")
    
    # Day headers
    week_header = ""
    for i in range(7):
        week_header += f" {german_days_short[i]:^3} "
    print(week_header)
    
    # Day numbers with today highlighted
    week_days = ""
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        if day.day == now.day:
            week_days += f"[{day.day:2d}] "  # Highlight today
        else:
            week_days += f" {day.day:2d}  "
    print(week_days)
    print("─────────────────────────────────")
    print()
    
    # Weather Section
    print("🌤️  WETTER HEUTE  🌤️")
    print("·································")
    print()
    
    # AI Brief
    print("💭 DEIN TAGESÜBERBLICK")
    print("═════════════════════════════════")
    print()
    print("Heute war ein produktiver Tag!")
    print("Das Wetter war sonnig mit 22°C.")
    print("Du hast 3 wichtige E-Mails erhalten")
    print("und 2 Termine erfolgreich absolviert.")
    print()
    
    # Tasks Section
    print("┌─────────────────────────────────┐")
    print("│        ✓ AUFGABEN HEUTE         │")
    print("└─────────────────────────────────┘")
    print()
    print("◆ E-Mail an Team senden")
    print()
    print("◆ Projektplan aktualisieren")
    print()
    print("◇ Code Review durchführen")
    print()
    print("── 3 Aufgaben insgesamt ──")
    print()
    
    # Shopping List
    print("╭─────────────────────────────────╮")
    print("│      🛒 EINKAUFSLISTE 🛒        │")
    print("╰─────────────────────────────────╯")
    print()
    print("  □ Milch")
    print("  □ Brot")
    print("  □ Äpfel")
    print("  □ Kaffee")
    print()
    print("── 4 Artikel ──")
    print()
    
    # Motivational Quote
    quotes = [
        "»Der beste Weg ist immer vorwärts«",
        "»Heute ist dein Tag!«",
        "»Klein anfangen, groß erreichen«"
    ]
    quote = random.choice(quotes)
    
    print("✨ ─────────────────────────── ✨")
    print(f"{quote}")
    print("✨ ─────────────────────────── ✨")
    print()
    
    # Footer
    gen_time = now.strftime("%H:%M")
    print("╔═══════════════════════════════════╗")
    print(f"║  Erstellt um {gen_time} Uhr         ║")
    print("║  © 2025 AI Daily Brief System     ║")
    print("╚═══════════════════════════════════╝")
    print()
    
    print("\n" + "="*40)
    print("KEY IMPROVEMENTS:")
    print("="*40)
    print("✅ Beautiful ASCII art borders")
    print("✅ Week calendar view with highlighted today")
    print("✅ Weather section indicator")
    print("✅ Improved task hierarchy (◆ for priority, ◇ for regular)")
    print("✅ Shopping list in card-style layout")
    print("✅ Motivational quotes section")
    print("✅ Professional footer with timestamp")
    print("✅ Better visual separation between sections")
    print("✅ Two-column layout for long shopping lists")
    print("✅ Smart text wrapping for long items")

if __name__ == "__main__":
    preview_receipt()
