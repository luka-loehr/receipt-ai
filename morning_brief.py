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

# Mock email data (replace with real data from email API)
MOCK_EMAILS = [
    {
        "from": "Team Slack",
        "subject": "Weekly product sync notes",
        "summary": "Q3 roadmap on track. New feature launch delayed by 1 week. Customer feedback positive.",
        "priority": "high",
        "time": "8:45 AM"
    },
    {
        "from": "Sarah Chen",
        "subject": "Re: Project timeline",
        "summary": "Confirmed meeting for Tuesday 2pm. Need final designs by EOW.",
        "priority": "high",
        "time": "9:12 AM"
    },
    {
        "from": "GitHub",
        "subject": "3 new PRs ready for review",
        "summary": "Frontend refactor PR merged. Two backend PRs awaiting your review.",
        "priority": "medium",
        "time": "7:30 AM"
    },
    {
        "from": "Calendar",
        "subject": "Today: 4 meetings scheduled",
        "summary": "10am Standup • 11am Client call • 2pm Design review • 4pm 1-on-1",
        "priority": "high",
        "time": "6:00 AM"
    },
    {
        "from": "AWS",
        "subject": "Monthly usage report",
        "summary": "Total spend $847. 12% decrease from last month. All services healthy.",
        "priority": "low",
        "time": "Yesterday"
    },
    {
        "from": "Newsletter Daily",
        "subject": "Tech news digest",
        "summary": "Apple announces new API. OpenAI updates GPT. Startup raises $50M Series B.",
        "priority": "low",
        "time": "5:00 AM"
    }
]

# Weather mock data
WEATHER = {
    "temp": "72°F",
    "condition": "Partly Cloudy",
    "high": "78°F",
    "low": "65°F"
}

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
    
    # macOS font paths with better options
    font_options = [
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
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(size))
    except:
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
    """Get time-appropriate greeting"""
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def get_priority_symbol(priority):
    """Get visual indicator for priority"""
    # Using ASCII characters for better compatibility
    symbols = {
        "high": "[!]",
        "medium": "[*]",
        "low": "[ ]"
    }
    return symbols.get(priority, "[ ]")

def create_morning_brief():
    """Generate the morning briefing receipt with high quality rendering"""
    # Start with tall canvas at higher resolution
    canvas_height = 2500 * DPI_SCALE
    img = Image.new("RGB", (PAPER_WIDTH, canvas_height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Load fonts with better sizes for clarity
    font_title = load_font(26, bold=True)
    font_heading = load_font(20, bold=True)
    font_normal = load_font(16)
    font_small = load_font(14)
    font_tiny = load_font(12)
    font_mono = load_font(14, mono=True)
    
    y = MARGIN
    
    # Decorative top border
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    
    # Main greeting
    greeting = f"{get_greeting()}, {USER_NAME}"
    y += draw_centered_text(draw, y, greeting, font_title)
    y += 15 * DPI_SCALE
    
    # Subtitle
    y += draw_centered_text(draw, y, "Your Daily Morning Brief", font_normal, GRAY_COLOR)
    y += 10 * DPI_SCALE
    
    # Date and time
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    y += draw_centered_text(draw, y, date_str, font_small)
    y += 20 * DPI_SCALE
    
    # Decorative separator
    y += draw_separator(draw, y, "solid", 2 * DPI_SCALE)
    y += 20 * DPI_SCALE
    
    # Weather section (using text instead of emoji for better compatibility)
    draw.text((MARGIN, y), "TODAY'S WEATHER", fill=FG_COLOR, font=font_heading)
    y += 35 * DPI_SCALE
    
    weather_line1 = f"{WEATHER['temp']} - {WEATHER['condition']}"
    draw.text((MARGIN + 20 * DPI_SCALE, y), weather_line1, fill=FG_COLOR, font=font_normal)
    y += 30 * DPI_SCALE
    
    weather_line2 = f"High: {WEATHER['high']}  Low: {WEATHER['low']}"
    draw.text((MARGIN + 20 * DPI_SCALE, y), weather_line2, fill=GRAY_COLOR, font=font_small)
    y += 35 * DPI_SCALE
    
    # Separator
    y += draw_separator(draw, y, "dashed")
    y += 20 * DPI_SCALE
    
    # Email summary section
    draw.text((MARGIN, y), "EMAIL HIGHLIGHTS", fill=FG_COLOR, font=font_heading)
    y += 35 * DPI_SCALE
    
    # Statistics
    high_priority = sum(1 for e in MOCK_EMAILS if e["priority"] == "high")
    total = len(MOCK_EMAILS)
    stats_text = f"{total} new - {high_priority} urgent"
    draw.text((MARGIN + 20 * DPI_SCALE, y), stats_text, fill=GRAY_COLOR, font=font_small)
    y += 35 * DPI_SCALE
    
    # Individual emails
    for i, email in enumerate(MOCK_EMAILS):
        if i > 0:
            y += 10 * DPI_SCALE  # Larger gap between emails
        
        # Priority indicator + sender
        priority_symbol = get_priority_symbol(email["priority"])
        sender_line = f"{priority_symbol} {email['from']}"
        draw.text((MARGIN, y), sender_line, fill=FG_COLOR, font=font_normal)
        
        # Time (right-aligned)
        time_bbox = draw.textbbox((0, 0), email["time"], font=font_tiny)
        time_width = time_bbox[2] - time_bbox[0]
        draw.text((PAPER_WIDTH - MARGIN - time_width, y), email["time"], fill=GRAY_COLOR, font=font_tiny)
        y += 28 * DPI_SCALE
        
        # Subject (indented)
        subject_text = email["subject"]
        if len(subject_text) > 35:
            subject_text = subject_text[:32] + "..."
        draw.text((MARGIN + 30 * DPI_SCALE, y), subject_text, fill=FG_COLOR, font=font_small)
        y += 26 * DPI_SCALE
        
        # Summary (wrapped, indented)
        y += draw_wrapped_text(draw, MARGIN + 30 * DPI_SCALE, y, email["summary"], 
                              font_tiny, PAPER_WIDTH - MARGIN * 2 - 30 * DPI_SCALE, GRAY_COLOR)
        y += 15 * DPI_SCALE
    
    y += 6
    
    # Separator before footer
    y += draw_separator(draw, y, "solid")
    y += 10
    
    # Tasks/Reminders section
    draw.text((MARGIN, y), "QUICK REMINDERS", fill=FG_COLOR, font=font_heading)
    y += 35 * DPI_SCALE
    
    reminders = [
        "- Standup meeting at 10:00 AM",
        "- Review pull requests before lunch",
        "- Submit expense report (due today)",
    ]
    
    for reminder in reminders:
        draw.text((MARGIN + 20 * DPI_SCALE, y), reminder, fill=FG_COLOR, font=font_small)
        y += 28 * DPI_SCALE
    
    y += 10
    
    # Separator
    y += draw_separator(draw, y, "dashed")
    y += 10
    
    # Daily quote
    quote = random.choice(QUOTES)
    y += draw_wrapped_text(draw, MARGIN, y, quote, font_tiny, 
                          PAPER_WIDTH - MARGIN * 2, GRAY_COLOR)
    
    y += 12
    
    # Bottom decorative border
    y += draw_decorative_border(draw, y)
    y += 8
    
    # Footer
    y += draw_centered_text(draw, y, "Have a productive day!", font_small, GRAY_COLOR)
    y += 4
    
    # Generation timestamp
    gen_time = now.strftime("%I:%M %p")
    y += draw_centered_text(draw, y, f"Generated at {gen_time}", font_tiny, GRAY_COLOR)
    
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
    
    # Auto-open on macOS
    try:
        import subprocess
        import sys
        if sys.platform == "darwin":
            subprocess.run(["open", OUTPUT_FILE])
    except:
        pass

if __name__ == "__main__":
    main()
