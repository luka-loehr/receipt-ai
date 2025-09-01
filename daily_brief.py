#!/usr/bin/env python3
"""
Daily Brief Generator — Personalized Daily Summary Receipt
Creates a beautiful 58mm thermal printer briefing with your daily overview
"""

from PIL import Image, ImageDraw, ImageFont
import datetime
import textwrap
import os
import random
import platform

# ============== CONFIGURATION ==============
USER_NAME = "Luka"
OUTPUT_FILE_PNG = "outputs/png/daily_brief.png"
OUTPUT_FILE_TXT = "outputs/txt/daily_brief.txt"

# Import real data services
from data_services import DataManager, WeatherData, EmailData, CalendarEvent, TaskData

# Initialize data manager
data_manager = DataManager()

# Quote of the day
QUOTES = [
    "\"The only way to do great work is to love what you do.\" — Steve Jobs",
    "\"Focus on being productive instead of busy.\" — Tim Ferriss",
    "\"The future depends on what you do today.\" — Mahatma Gandhi",
    "\"Simplicity is the ultimate sophistication.\" — Leonardo da Vinci",
]
# ============================================

# Constants for 58mm thermal printer
# Using 2x resolution for better quality, then downscale
DPI_SCALE = 2  # Render at 2x for better quality
PAPER_WIDTH = 384 * DPI_SCALE  # pixels at 203 dpi * scale
FINAL_WIDTH = 384  # Final output width
MARGIN = 8 * DPI_SCALE  # Minimal margin for maximum text space
BG_COLOR = "white"
FG_COLOR = "black"
GRAY_COLOR = "#666666"

def load_font(size=16, bold=False, mono=False):
    """Load fonts using cross-platform compatible approach with Unicode support"""
    # Scale font size for higher DPI
    size = size * DPI_SCALE
    
    # Try to find a system font that supports German characters
    font_paths = []
    
    # Common system fonts that support international characters
    if os.name == 'nt':  # Windows
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\calibri.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf"
        ]
    elif os.name == 'posix':  # macOS and Linux
        if platform.system() == 'Darwin':  # macOS
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
            ]
    
    # Try to load a system font
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, int(size))
            except Exception:
                continue
    
    # Fallback to default font if no system fonts found
    try:
        return ImageFont.load_default(size=int(size))
    except Exception:
        return ImageFont.load_default()

def draw_centered_text(draw, y, text, font, color=FG_COLOR):
    """Draw centered text"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (PAPER_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]

def draw_wrapped_text(draw, x, y, text, font, max_width, color=FG_COLOR, line_spacing_multiplier=1.4):
    """Draw text with aggressive width utilization"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Test if adding this word would exceed width
        test_line = current_line + (" " if current_line else "") + word
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = test_bbox[2] - test_bbox[0]
        
        if test_width <= max_width:
            current_line = test_line
        else:
            # Line would be too long, start new line
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Single word is too long, force it anyway
                lines.append(word)
                current_line = ""
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    total_height = 0
    for i, line in enumerate(lines):
        draw.text((x, y), line, fill=color, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        
        # Apply line spacing multiplier for better readability
        spacing = int(line_height * line_spacing_multiplier)
        y += spacing
        total_height += spacing
    
    return total_height

def draw_separator(draw, y, style="solid", width=1):
    """Draw a separator line"""
    if style == "solid":
        draw.line([(MARGIN, y), (PAPER_WIDTH - MARGIN, y)], fill=FG_COLOR, width=width)
    elif style == "dashed":
        for x in range(MARGIN, PAPER_WIDTH - MARGIN, 8):
            draw.line([(x, y), (min(x + 4, PAPER_WIDTH - MARGIN), y)], fill=FG_COLOR, width=width)
    elif style == "dotted":
        for x in range(MARGIN, PAPER_WIDTH - MARGIN, 6):
            draw.ellipse([(x, y-1), (x+2, y+1)], fill=FG_COLOR)
    return width + 2

def draw_decorative_border(draw, y, height=3):
    """Draw a decorative border pattern"""
    pattern = "▪ □ ▪"
    for i in range(3):
        draw.line([(MARGIN, y + i), (PAPER_WIDTH - MARGIN, y + i)], fill=FG_COLOR, width=1)
    return height + 2

def get_greeting():
    """Get AI-generated time-appropriate greeting in German"""
    # This will be called after the brief is generated, so we can use the cached response
    return data_manager._cached_brief_response.greeting

def get_priority_symbol(priority):
    """Get visual indicator for priority"""
    # Using ASCII characters for better compatibility
    symbols = {
        "high": "[!]",
        "medium": "[*]",
        "low": "[ ]"
    }
    return symbols.get(priority, "[ ]")

def generate_german_overview(emails, events):
    """Backward-compat wrapper kept for safety; actual overview is generated via AIService in DataManager."""
    try:
        # Use DataManager's AI service to generate the overview when available
        # We can't import the manager globally here due to ordering; use the existing instance
        return data_manager.ai_service.generate_german_overview(emails, events, user_name=USER_NAME)
    except Exception as e:
        print(f"⚠️  German overview generation error: {e}")
        # Minimal fallback
        total_emails = len(emails)
        event_count = len(events)
        return f"Guten Morgen {USER_NAME}! Du hast {total_emails} neue E-Mails und {event_count} Termine."

def generate_text_brief(brief_response, ai_brief):
    """Generate a plain text version that matches exactly what's on the PNG"""
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %d. %B %Y")
    time_str = now.strftime("%H:%M")
    
    # Get tasks if available (same logic as PNG generation)
    tasks_text = ""
    if hasattr(data_manager, 'task_service'):
        try:
            tasks = data_manager.task_service.get_tasks()
            if tasks:
                tasks_text = "\n✅ AUFGABEN\n\n"
                for i, task in enumerate(tasks[:5], 1):
                    priority_symbol = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                    # Use the same truncation logic as PNG (50 chars max)
                    task_title = task.title
                    if len(f"{priority_symbol} {task_title}") > 50:
                        task_title = task_title[:47] + "..."
                    tasks_text += f"☐ {priority_symbol} {task_title}\n"
        except Exception as e:
            print(f"⚠️  Error generating tasks for text: {e}")
    
    # Create text content that matches PNG exactly
    text_content = f"""{brief_response.greeting}

KI-Tagesbrief

{date_str}

{ai_brief}

{tasks_text}
Erstellt um {time_str}"""
    
    # Save text file
    with open(OUTPUT_FILE_TXT, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"📝 Text brief created: {OUTPUT_FILE_TXT}")

def create_daily_brief():
    """Generate the simplified AI-powered daily briefing receipt"""
    # Fetch AI-generated comprehensive brief and greeting in one call
    print("🔄 Generating AI brief and greeting...")
    brief_response = data_manager.get_daily_brief(USER_NAME)
    
    # Cache the response for the greeting function
    data_manager._cached_brief_response = brief_response
    ai_brief = brief_response.brief
    
    # Also generate text version that matches PNG exactly
    generate_text_brief(brief_response, ai_brief)
    
    # Start with smaller canvas at higher resolution
    canvas_height = 1000 * DPI_SCALE
    img = Image.new("RGB", (PAPER_WIDTH, canvas_height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Load fonts with better sizes for clarity
    font_title = load_font(26, bold=True)
    font_normal = load_font(16)
    font_small = load_font(14)
    font_tiny = load_font(12)
    
    y = MARGIN
    
    # Decorative top border
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    
    # Main greeting
    greeting = get_greeting()
    y += draw_centered_text(draw, y, greeting, font_title)
    y += 15 * DPI_SCALE
    
    # Subtitle
    y += draw_centered_text(draw, y, "KI-Tagesbrief", font_normal, GRAY_COLOR)
    y += 10 * DPI_SCALE
    
    # Date and time
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %d. %B %Y")
    y += draw_centered_text(draw, y, date_str, font_small)
    y += 20 * DPI_SCALE
    
    # Decorative separator
    y += draw_separator(draw, y, "solid", 2 * DPI_SCALE)
    y += 25 * DPI_SCALE
    
    # AI-generated comprehensive overview with optimized spacing
    y += draw_wrapped_text(draw, MARGIN, y, ai_brief, font_normal, 
                          PAPER_WIDTH - MARGIN * 2, FG_COLOR, line_spacing_multiplier=1.4)
    y += 25 * DPI_SCALE
    
    # Tasks Section
    if hasattr(data_manager, 'task_service'):
        try:
            tasks = data_manager.task_service.get_tasks()
            if tasks:
                # Section header
                y += draw_separator(draw, y, "dashed", 1 * DPI_SCALE)
                y += 15 * DPI_SCALE
                
                # "Aufgaben" title
                y += draw_centered_text(draw, y, "✅ AUFGABEN", font_small, GRAY_COLOR)
                y += 15 * DPI_SCALE
                
                # Draw tasks with checkboxes
                for i, task in enumerate(tasks[:5]):  # Limit to 5 tasks for space
                    # Checkbox (empty square)
                    checkbox_x = MARGIN + 10 * DPI_SCALE
                    checkbox_size = 12 * DPI_SCALE
                    draw.rectangle([checkbox_x, y, checkbox_x + checkbox_size, y + checkbox_size], 
                                 outline=FG_COLOR, width=1)
                    
                    # Priority indicator
                    priority_symbol = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                    
                    # Task text (with priority emoji)
                    task_text = f"{priority_symbol} {task.title}"
                    if len(task_text) > 50:  # Truncate long task names
                        task_text = task_text[:47] + "..."
                    
                    # Draw task text
                    draw.text((checkbox_x + checkbox_size + 8 * DPI_SCALE, y), task_text, 
                             fill=FG_COLOR, font=font_tiny)
                    
                    y += checkbox_size + 8 * DPI_SCALE
                    
                    # Add small spacing between tasks
                    if i < len(tasks) - 1:
                        y += 5 * DPI_SCALE
                
                y += 15 * DPI_SCALE
        except Exception as e:
            print(f"⚠️  Error displaying tasks: {e}")
    
    # Bottom decorative border
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    
    # Generation timestamp
    y += 8 * DPI_SCALE
    
    # Generation timestamp
    gen_time = now.strftime("%H:%M")
    y += draw_centered_text(draw, y, f"Erstellt um {gen_time}", font_tiny, GRAY_COLOR)
    
    y += MARGIN
    
    # Crop to content
    img = img.crop((0, 0, PAPER_WIDTH, y))
    
    # Downscale for better quality (anti-aliasing)
    if DPI_SCALE > 1:
        new_size = (FINAL_WIDTH, int(y / DPI_SCALE))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    return img

def main():
    """Generate and save the daily briefing"""
    print("📅  Generating your daily briefing...")
    
    # Create briefing
    brief_img = create_daily_brief()
    
    # Save
    brief_img.save(OUTPUT_FILE_PNG)
    
    # Success message
    print(f"✅ Daily brief created: {OUTPUT_FILE_PNG}")
    print(f"📐 Dimensions: {brief_img.width}x{brief_img.height}px")
    print(f"📄 Paper width: 58mm (384px)")
    print("\n☕ Perfect for your daily productivity ritual!")
    
    # Auto-open image
    try:
        import subprocess
        import sys
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", OUTPUT_FILE_PNG])
        elif sys.platform == "linux":
            # Try multiple Linux image viewers
            viewers = ["xdg-open", "display", "eog", "gthumb", "gimp"]
            for viewer in viewers:
                try:
                    subprocess.run([viewer, OUTPUT_FILE_PNG], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", OUTPUT_FILE_PNG], shell=True)
    except:
        pass

if __name__ == "__main__":
    main()
