#!/usr/bin/env python3
"""
Morning Brief Generator — Daily Email Summary Receipt
Creates a beautiful 58mm thermal printer briefing with your daily emails
"""

from PIL import Image, ImageDraw, ImageFont
import datetime
import textwrap
import os
import random
import platform

# ============== CONFIGURATION ==============
USER_NAME = "Luka"
OUTPUT_FILE = "morning_brief.png"

# Import real data services
from data_services import DataManager, WeatherData, EmailData, CalendarEvent

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
MARGIN = 15 * DPI_SCALE
BG_COLOR = "white"
FG_COLOR = "black"
GRAY_COLOR = "#666666"

def load_font(size=16, bold=False, mono=False):
    """Load appropriate fonts for the receipt with better quality"""
    # Scale font size for higher DPI
    size = size * DPI_SCALE
    
    # Linux font paths with better options (try these first)
    linux_font_options = [
        # DejaVu fonts (high quality, commonly available)
        {
            "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        },
        # Liberation fonts (good quality)
        {
            "regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "mono": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
        },
        # Ubuntu fonts
        {
            "regular": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            "bold": "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "mono": "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
        },
        # Free fonts
        {
            "regular": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "bold": "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "mono": "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        },
        # Noto fonts
        {
            "regular": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "bold": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "mono": "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
        }
    ]
    
    # macOS font paths with better options
    macos_font_options = [
        # SF Pro (Apple's system font) - best quality
        {
            "regular": "/System/Library/Fonts/SFNS.ttf",
            "bold": "/System/Library/Fonts/SFNS-Bold.ttf",
            "mono": "/System/Library/Fonts/Monaco.dfont"
        },
        # Helvetica Neue (high quality)
        {
            "regular": "/System/Library/Fonts/Helvetica.ttc",
            "bold": "/System/Library/Fonts/Helvetica.ttc",
            "mono": "/System/Library/Fonts/Menlo.ttc"
        },
        # Avenir (modern, clean)
        {
            "regular": "/System/Library/Fonts/Avenir Next.ttc",
            "bold": "/System/Library/Fonts/Avenir Next.ttc",
            "mono": "/System/Library/Fonts/Courier.dfont"
        },
        # System fonts
        {
            "regular": "/System/Library/Fonts/Supplemental/Arial.ttf",
            "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "mono": "/System/Library/Fonts/Supplemental/Courier New.ttf"
        }
    ]
    
    # Choose font options based on platform
    if platform.system() == "Linux":
        font_options = linux_font_options + macos_font_options
    else:
        font_options = macos_font_options
    
    # Determine which font type to load
    if mono:
        font_key = "mono"
    elif bold:
        font_key = "bold"
    else:
        font_key = "regular"
    
    # Try each font option
    for font_set in font_options:
        font_path = font_set[font_key]
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, int(size))
                # For fonts in TTC collections, try to get the right index
                if bold and font_path.endswith('.ttc'):
                    # Try bold variant index (usually 1 or 2)
                    try:
                        font = ImageFont.truetype(font_path, int(size), index=1)
                    except:
                        pass
                return font
            except Exception as e:
                continue
    
    # Fallback to PIL's better default
    try:
        from PIL import ImageFont
        if platform.system() == "Linux":
            # Try a common Linux font as fallback
            fallback_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
            for path in fallback_paths:
                if os.path.exists(path):
                    return ImageFont.truetype(path, int(size))
        else:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(size))
    except:
        pass
    
    # Ultimate fallback
    default = ImageFont.load_default()
    # Try to scale the default font
    return default

def draw_centered_text(draw, y, text, font, color=FG_COLOR):
    """Draw centered text"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (PAPER_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]

def draw_wrapped_text(draw, x, y, text, font, max_width, color=FG_COLOR):
    """Draw text with word wrapping"""
    # Calculate approximate character width
    test_bbox = draw.textbbox((0, 0), "M", font=font)
    char_width = test_bbox[2] - test_bbox[0]
    chars_per_line = max_width // char_width
    
    # Wrap text
    lines = textwrap.wrap(text, width=chars_per_line)
    
    total_height = 0
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        y += line_height + 2
        total_height += line_height + 2
    
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
    """Get time-appropriate greeting in German"""
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Guten Morgen"
    elif hour < 17:
        return "Guten Tag"
    else:
        return "Guten Abend"

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

def create_morning_brief():
    """Generate the simplified AI-powered morning briefing receipt"""
    # Fetch AI-generated comprehensive brief
    print("🔄 Generating AI brief...")
    ai_brief = data_manager.get_comprehensive_brief(USER_NAME)
    
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
    greeting = f"{get_greeting()}, {USER_NAME}"
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
    
    # AI-generated comprehensive overview
    y += draw_wrapped_text(draw, MARGIN, y, ai_brief, font_normal, 
                          PAPER_WIDTH - MARGIN * 2, FG_COLOR)
    y += 25 * DPI_SCALE
    
    # Bottom decorative border
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    
    # Footer
    y += draw_centered_text(draw, y, "Hab einen produktiven Tag!", font_small, GRAY_COLOR)
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
    """Generate and save the morning briefing"""
    print("☀️  Generating your morning briefing...")
    
    # Create briefing
    brief_img = create_morning_brief()
    
    # Save
    brief_img.save(OUTPUT_FILE)
    
    # Success message
    print(f"✅ Morning brief created: {OUTPUT_FILE}")
    print(f"📐 Dimensions: {brief_img.width}x{brief_img.height}px")
    print(f"📄 Paper width: 58mm (384px)")
    print("\n☕ Perfect for your morning coffee ritual!")
    
    # Auto-open image
    try:
        import subprocess
        import sys
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", OUTPUT_FILE])
        elif sys.platform == "linux":
            # Try multiple Linux image viewers
            viewers = ["xdg-open", "display", "eog", "gthumb", "gimp"]
            for viewer in viewers:
                try:
                    subprocess.run([viewer, OUTPUT_FILE], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", OUTPUT_FILE], shell=True)
    except:
        pass

if __name__ == "__main__":
    main()
