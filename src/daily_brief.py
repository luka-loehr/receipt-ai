#!/usr/bin/env python3
"""
Daily Brief Generator — Personalized Daily Summary Receipt
Creates a beautiful 58mm thermal printer briefing with your daily overview using modular architecture
"""

from PIL import Image, ImageDraw, ImageFont
import datetime
import textwrap
import os
import random
import platform

# Import modular system
from .config import AppConfig, get_config
from .models import CompleteReceiptContent, PrintableContent
from .data_manager import ModularDataManager, get_data_manager

# Initialize with configuration
config = get_config()
data_manager = get_data_manager()

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

# ============== THERMAL PRINTER SUPPORT ==============

def get_printer_config():
    """Get printer configuration from environment or config file"""
    try:
        from .printer_config import PRINTER_CONFIGS
        
        # Check if user has a preferred printer config
        printer_type = os.getenv('THERMAL_PRINTER_TYPE', 'file_test')
        
        if printer_type in PRINTER_CONFIGS:
            return PRINTER_CONFIGS[printer_type]
        else:
            print(f"⚠️  Printer config '{printer_type}' not found, using file_test")
            return PRINTER_CONFIGS['file_test']
            
    except ImportError:
        print("⚠️  printer_config.py not found, using file-based printer")
        from .thermal_printer import PrinterConfig
        return PrinterConfig(
            connection_type='file',
            device_id='outputs/escpos/daily_brief.txt'
        )

def print_to_thermal_printer(greeting, brief, tasks=None):
    """Print the daily brief to thermal printer using ESC/POS"""
    try:
        from .thermal_printer import ThermalPrinter
        
        # Get printer configuration
        config = get_printer_config()
        
        # Create output directory for file-based printing
        if config.connection_type == 'file':
            os.makedirs('outputs/escpos', exist_ok=True)
        
        # Connect to printer
        printer = ThermalPrinter(config)
        
        if printer.is_connected():
            print("🖨️  Printing to thermal printer...")
            
            # Convert tasks to list of strings if available
            task_list = []
            if tasks:
                print(f"📋 Printing {len(tasks)} tasks...")
                for i, task in enumerate(tasks):
                    task_title = task.title if hasattr(task, 'title') else str(task)
                    
                    # Apply the EXACT same logic as PNG/TXT preview
                    if len(task_title) > 70:
                        # Find the last complete word that fits within 70 chars
                        max_chars = 67  # Leave room for "..."
                        words = task_title.split()
                        truncated_title = ""
                        for word in words:
                            if len(truncated_title + " " + word) <= max_chars:
                                truncated_title += (" " if truncated_title else "") + word
                            else:
                                break
                        final_title = truncated_title + "..." if truncated_title else task_title[:67] + "..."
                    else:
                        final_title = task_title
                    
                    task_list.append(final_title)
            
            # Convert shopping list to list of strings if available
            shopping_list = []
            if hasattr(data_manager, 'shopping_list') and data_manager.shopping_list:
                print(f"🛒 Printing {len(data_manager.shopping_list)} shopping items...")
                for i, item in enumerate(data_manager.shopping_list):
                    item_title = item.title if hasattr(item, 'title') else str(item)
                    
                    # Apply the EXACT same logic as tasks
                    if len(item_title) > 70:
                        # Find the last complete word that fits within 70 chars
                        max_chars = 67  # Leave room for "..."
                        words = item_title.split()
                        truncated_title = ""
                        for word in words:
                            if len(truncated_title + " " + word) <= max_chars:
                                truncated_title += (" " if truncated_title else "") + word
                            else:
                                break
                        final_title = truncated_title + "..." if truncated_title else item_title[:67] + "..."
                    else:
                        final_title = item_title
                    
                    shopping_list.append(final_title)
            
            # Print the daily brief
            success = printer.print_daily_brief(greeting, brief, task_list, shopping_list)
            
            if success:
                print("✅ Daily brief printed successfully!")
            else:
                print("❌ Printing failed")
            
            printer.disconnect()
            return success
        else:
            print("❌ Could not connect to thermal printer")
            return False
            
    except ImportError:
        print("⚠️  Thermal printer support not available. Install with: pip install python-escpos")
        return False
    except Exception as e:
        print(f"❌ Thermal printer error: {e}")
        return False

# ============== EXISTING FUNCTIONS (unchanged) ==============

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
    """Get hardcoded time-appropriate greeting in German"""
    import datetime
    
    current_hour = datetime.datetime.now().hour
    user_name = config.user_name
    
    if 5 <= current_hour < 12:
        return f"Guten Morgen, {user_name}!"
    elif 12 <= current_hour < 17:
        return f"Guten Tag, {user_name}!"
    elif 17 <= current_hour < 22:
        return f"Guten Abend, {user_name}!"
    else:
        return f"Gute Nacht, {user_name}!"

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
        return data_manager.ai_service.generate_german_overview(emails, events, user_name=config.user_name)
    except Exception as e:
        print(f"⚠️  German overview generation error: {e}")
        # Minimal fallback
        total_emails = len(emails)
        event_count = len(events)
        greeting = get_greeting()
        return f"{greeting} Du hast {total_emails} neue E-Mails und {event_count} Termine."

def generate_text_brief(brief_response, ai_brief):
    """Generate a plain text version that matches exactly what's on the PNG"""
    import locale
    
    # Set German locale for date formatting
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'de_DE')
        except locale.Error:
            # Fallback to manual German month/day names
            pass
    
    now = datetime.datetime.now()
    
    # German month and day names
    german_months = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
        7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    german_days = {
        0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 
        4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
    }
    
    # Create German date string
    day_name = german_days[now.weekday()]
    month_name = german_months[now.month]
    date_str = f"{day_name}, {now.day}. {month_name} {now.year}"
    time_str = now.strftime("%H:%M")
    
    # Get tasks if available (same logic as PNG generation)
    tasks_text = ""
    if hasattr(data_manager, 'task_service'):
        try:
            tasks = data_manager.task_service.get_tasks()
            if tasks:
                tasks_text = "\n✅ AUFGABEN\n\n"
                for i, task in enumerate(tasks, 1):
                    # Use the same truncation logic as PNG (70 chars max) with smart word handling
                    task_title = task.title
                    if len(task_title) > 70:
                        # Find the last complete word that fits within 70 chars
                        max_chars = 67  # Leave room for "..."
                        words = task.title.split()
                        truncated_title = ""
                        for word in words:
                            if len(truncated_title + " " + word) <= max_chars:
                                truncated_title += (" " if truncated_title else "") + word
                            else:
                                break
                        task_title = truncated_title + "..." if truncated_title else task.title[:67] + "..."
                    tasks_text += f"{task_title}\n"
        except Exception as e:
            print(f"⚠️  Error generating tasks for text: {e}")
    
    # Get shopping list if available
    shopping_text = ""
    if hasattr(data_manager, 'shopping_list') and data_manager.shopping_list:
        try:
            shopping_text = "\n🛒 EINKAUFSLISTE\n\n"
            for i, item in enumerate(data_manager.shopping_list, 1):
                # Use the same truncation logic as tasks
                item_title = item.title
                if len(item_title) > 70:
                    # Find the last complete word that fits within 70 chars
                    max_chars = 67  # Leave room for "..."
                    words = item.title.split()
                    truncated_title = ""
                    for word in words:
                        if len(truncated_title + " " + word) <= max_chars:
                            truncated_title += (" " if truncated_title else "") + word
                        else:
                            break
                    item_title = truncated_title + "..." if truncated_title else item.title[:67] + "..."
                shopping_text += f"{item_title}\n"
        except Exception as e:
            print(f"⚠️  Error generating shopping list for text: {e}")
    
    # Create text content that matches PNG exactly
    greeting = get_greeting()
    text_content = f"""{greeting}

KI-Tagesbrief

{date_str}

{ai_brief}

{tasks_text}{shopping_text}
Erstellt um {time_str}"""
    
    # Save text file
    with open(config.output_txt_file, 'w', encoding='utf-8') as f:
        f.write(text_content)
    


def create_daily_brief():
    """Generate the AI-powered daily briefing receipt using modular system"""
    # Generate complete AI-powered receipt content
    receipt_content = data_manager.generate_complete_receipt()
    
    # Format for printing 
    printable_content = data_manager.format_for_printing(
        receipt_content,
        tasks=[], # Tasks will be handled by the receipt content
        shopping_items=[]  # Shopping items will be handled by the receipt content
    )
    
    # Also generate text version that matches PNG exactly
    generate_text_brief(receipt_content, receipt_content.summary.brief)
    
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
    
    # AI-generated greeting
    y += draw_centered_text(draw, y, receipt_content.header.greeting, font_title)
    y += 15 * DPI_SCALE
    
    # AI-generated subtitle
    y += draw_centered_text(draw, y, receipt_content.header.title, font_normal, GRAY_COLOR)
    y += 10 * DPI_SCALE
    
    # AI-generated date
    y += draw_centered_text(draw, y, receipt_content.header.date_formatted, font_small)
    y += 20 * DPI_SCALE
    
    # Decorative separator
    y += draw_separator(draw, y, "solid", 2 * DPI_SCALE)
    y += 25 * DPI_SCALE
    
    # AI-generated comprehensive overview with optimized spacing
    y += draw_wrapped_text(draw, MARGIN, y, receipt_content.summary.brief, font_normal, 
                          PAPER_WIDTH - MARGIN * 2, FG_COLOR, line_spacing_multiplier=1.4)
    y += 25 * DPI_SCALE
    
    # Tasks Section
    tasks = []
    original_tasks = []  # Store original untruncated tasks
    if receipt_content.task_section and printable_content.printable_tasks:
        try:
            # Get raw task data for thermal printer
            _, _, _, raw_tasks, _ = data_manager.fetch_all_data()
            original_tasks = raw_tasks
            tasks = printable_content.printable_tasks
            
            if tasks:
                # Section header
                y += draw_separator(draw, y, "dashed", 1 * DPI_SCALE)
                y += 15 * DPI_SCALE
                
                # AI-generated section title
                y += draw_centered_text(draw, y, receipt_content.task_section.section_title, font_small, GRAY_COLOR)
                y += 15 * DPI_SCALE
                
                # Draw tasks with checkboxes
                for i, task in enumerate(tasks):
                    # Checkbox (empty square)
                    checkbox_x = MARGIN + 10 * DPI_SCALE
                    checkbox_size = 12 * DPI_SCALE
                    draw.rectangle([checkbox_x, y, checkbox_x + checkbox_size, y + checkbox_size], 
                                 outline=FG_COLOR, width=1)
                    
                    # Use pre-formatted task text from printable content
                    task_text = task.display_text
                    
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
    
    # Shopping List Section  
    if receipt_content.shopping_section and printable_content.printable_shopping:
        try:
            # Section header
            y += draw_separator(draw, y, "dashed", 1 * DPI_SCALE)
            y += 15 * DPI_SCALE
            
            # AI-generated section title
            y += draw_centered_text(draw, y, receipt_content.shopping_section.section_title, font_small, GRAY_COLOR)
            y += 15 * DPI_SCALE
            
            # Draw shopping list items with checkboxes
            for i, item in enumerate(printable_content.printable_shopping):
                # Checkbox (empty square)
                checkbox_x = MARGIN + 10 * DPI_SCALE
                checkbox_size = 12 * DPI_SCALE
                draw.rectangle([checkbox_x, y, checkbox_x + checkbox_size, y + checkbox_size], 
                             outline=FG_COLOR, width=1)
                
                # Use pre-formatted item text from printable content
                item_text = item.display_text
                
                # Draw item text
                draw.text((checkbox_x + checkbox_size + 8 * DPI_SCALE, y), item_text, 
                         fill=FG_COLOR, font=font_tiny)
                
                y += checkbox_size + 8 * DPI_SCALE
                
                # Add small spacing between items
                if i < len(printable_content.printable_shopping) - 1:
                    y += 5 * DPI_SCALE
            
            y += 15 * DPI_SCALE
        except Exception as e:
            print(f"⚠️  Error displaying shopping list: {e}")
    
    # Bottom decorative border
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    
    # AI-generated footer
    y += 8 * DPI_SCALE
    
    # AI-generated timestamp with label
    timestamp_text = f"{receipt_content.footer.timestamp_label} {receipt_content.footer.timestamp}"
    y += draw_centered_text(draw, y, timestamp_text, font_tiny, GRAY_COLOR)
    
    # Motivational note if available
    if receipt_content.footer.motivational_note:
        y += 8 * DPI_SCALE
        y += draw_centered_text(draw, y, receipt_content.footer.motivational_note, font_tiny, GRAY_COLOR)
    
    y += MARGIN
    
    # Crop to content
    img = img.crop((0, 0, PAPER_WIDTH, y))
    
    # Downscale for better quality (anti-aliasing)
    if DPI_SCALE > 1:
        new_size = (FINAL_WIDTH, int(y / DPI_SCALE))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    return img, receipt_content, original_tasks

def main():
    """Generate and save the daily briefing, then print to thermal printer"""
    print("📅  Generating your daily briefing...")
    
    # Create briefing (now returns image, brief_response, and tasks)
    brief_img, brief_response, tasks = create_daily_brief()
    
    # Save PNG
    brief_img.save(config.output_png_file)
    
    # Success message
    print(f"✅ Daily brief created")
    
    # Print to thermal printer
    print("\n🖨️  Printing to thermal printer...")
    greeting = brief_response.header.greeting
    brief = brief_response.summary.brief
    
    # Show what tasks are being sent to printer
    if tasks:
        print(f"📋 Sending {len(tasks)} tasks to printer...")
    
    print_to_thermal_printer(greeting, brief, tasks)
    
    print("\n☕ Perfect for your daily productivity ritual!")
    
    # Auto-open image
    try:
        import subprocess
        import sys
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", config.output_png_file])
        elif sys.platform == "linux":
            # Try multiple Linux image viewers
            viewers = ["xdg-open", "display", "eog", "gthumb", "gimp"]
            for viewer in viewers:
                try:
                    subprocess.run([viewer, config.output_png_file], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", config.output_png_file], shell=True)
    except:
        pass

if __name__ == "__main__":
    main()
