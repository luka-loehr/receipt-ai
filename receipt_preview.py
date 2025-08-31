#!/usr/bin/env python3
"""
Receipt Playground — Barcode & Receipt Preview Generator
Creates a PNG preview of receipts with barcodes (58mm thermal printer width)
Iterate quickly without wasting paper!
"""

from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# ============== CONFIGURATION (edit these to iterate) ==============
# Barcode settings
BARCODE_TYPE = "CODE128"  # Options: EAN13, CODE128, CODE39, QR
BARCODE_DATA = "RCPT-2025-001234"  # Your barcode data
BAR_HEIGHT = 100  # Height of barcode in pixels
BAR_MODULE_WIDTH = 2  # Width of smallest bar element

# Receipt content
STORE_NAME = "RECEIPT PLAYGROUND"
STORE_ADDRESS = "Thermal Printer Preview"
ITEMS = [
    {"name": "Test Item 1", "price": 12.99, "qty": 2},
    {"name": "Sample Product", "price": 5.50, "qty": 1},
    {"name": "Demo Service", "price": 25.00, "qty": 1},
]
TAX_RATE = 0.08  # 8% tax
FOOTER_TEXT = "Thank you for testing!"

# Output settings
OUTPUT_FILE = "receipt_preview.png"
SHOW_TIMESTAMP = True
# ====================================================================

# Constants for 58mm thermal printer
PAPER_WIDTH = 384  # pixels at 203 dpi (58mm printable area)
MARGIN = 20
BG_COLOR = "white"
FG_COLOR = "black"
LINE_SPACING = 5

def load_font(size=16):
    """Try to load a monospace font, fallback to default"""
    font_paths = [
        "/System/Library/Fonts/Courier.dfont",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "C:\\Windows\\Fonts\\consola.ttf",  # Windows
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    
    # Fallback to default
    return ImageFont.load_default()

def draw_barcode_placeholder(draw, x, y, width, height, data, barcode_type):
    """Draw a barcode placeholder or actual barcode if library available"""
    try:
        # Try to use python-barcode if available
        import barcode
        from barcode.writer import ImageWriter
        from io import BytesIO
        
        # Generate actual barcode
        if barcode_type == "EAN13" and len(data) == 12:
            data = data + "0"  # Add check digit
            code = barcode.EAN13(data, writer=ImageWriter())
        elif barcode_type == "CODE128":
            code = barcode.Code128(data, writer=ImageWriter())
        elif barcode_type == "CODE39":
            code = barcode.Code39(data, writer=ImageWriter())
        else:
            raise ImportError("Unsupported barcode type")
        
        # Render to image
        rv = BytesIO()
        code.write(rv, options={"module_width": BAR_MODULE_WIDTH/10, "module_height": height/10})
        barcode_img = Image.open(rv)
        
        # Calculate position to center the barcode
        barcode_width = min(barcode_img.width, width)
        barcode_img = barcode_img.resize((barcode_width, height), Image.Resampling.LANCZOS)
        
        return barcode_img, (x + (width - barcode_width) // 2, y)
        
    except ImportError:
        # Draw placeholder if barcode library not available
        # Draw barcode simulation (alternating bars)
        bar_count = min(len(data) * 7, 50)  # Approximate bar count
        bar_width = width // bar_count
        
        for i in range(bar_count):
            if i % 2 == 0:
                draw.rectangle([x + i * bar_width, y, x + (i + 1) * bar_width, y + height], 
                             fill=FG_COLOR)
        
        # Draw border
        draw.rectangle([x, y, x + width, y + height], outline=FG_COLOR, width=2)
        
        return None, None

def draw_centered_text(draw, y, text, font, color=FG_COLOR):
    """Draw centered text at given y position"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (PAPER_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]  # Return text height

def draw_line(draw, y, style="solid"):
    """Draw a horizontal line"""
    if style == "dashed":
        for x in range(MARGIN, PAPER_WIDTH - MARGIN, 10):
            draw.line([(x, y), (x + 5, y)], fill=FG_COLOR, width=1)
    else:
        draw.line([(MARGIN, y), (PAPER_WIDTH - MARGIN, y)], fill=FG_COLOR, width=1)
    return 1

def format_price(price):
    """Format price with two decimal places"""
    return f"${price:.2f}"

def create_receipt():
    """Generate the complete receipt preview"""
    # Start with a tall canvas, we'll crop later
    canvas_height = 2000
    img = Image.new("RGB", (PAPER_WIDTH, canvas_height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    font_large = load_font(20)
    font_normal = load_font(16)
    font_small = load_font(14)
    
    y_pos = MARGIN
    
    # Header
    y_pos += draw_centered_text(draw, y_pos, STORE_NAME, font_large)
    y_pos += LINE_SPACING
    y_pos += draw_centered_text(draw, y_pos, STORE_ADDRESS, font_small)
    y_pos += LINE_SPACING * 2
    
    # Timestamp
    if SHOW_TIMESTAMP:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        y_pos += draw_centered_text(draw, y_pos, timestamp, font_small)
        y_pos += LINE_SPACING * 2
    
    # Line separator
    y_pos += draw_line(draw, y_pos)
    y_pos += LINE_SPACING * 2
    
    # Items
    subtotal = 0
    for item in ITEMS:
        # Item name and quantity
        item_text = f"{item['name']} x{item['qty']}"
        draw.text((MARGIN, y_pos), item_text, fill=FG_COLOR, font=font_normal)
        
        # Price (right-aligned)
        item_total = item['price'] * item['qty']
        subtotal += item_total
        price_text = format_price(item_total)
        bbox = draw.textbbox((0, 0), price_text, font=font_normal)
        price_width = bbox[2] - bbox[0]
        draw.text((PAPER_WIDTH - MARGIN - price_width, y_pos), price_text, 
                 fill=FG_COLOR, font=font_normal)
        
        y_pos += bbox[3] - bbox[1] + LINE_SPACING
    
    y_pos += LINE_SPACING
    y_pos += draw_line(draw, y_pos, "dashed")
    y_pos += LINE_SPACING * 2
    
    # Totals
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    
    # Subtotal
    draw.text((MARGIN, y_pos), "Subtotal:", fill=FG_COLOR, font=font_normal)
    subtotal_text = format_price(subtotal)
    bbox = draw.textbbox((0, 0), subtotal_text, font=font_normal)
    draw.text((PAPER_WIDTH - MARGIN - bbox[2] + bbox[0], y_pos), subtotal_text, 
             fill=FG_COLOR, font=font_normal)
    y_pos += bbox[3] - bbox[1] + LINE_SPACING
    
    # Tax
    draw.text((MARGIN, y_pos), f"Tax ({TAX_RATE*100:.0f}%):", fill=FG_COLOR, font=font_normal)
    tax_text = format_price(tax)
    bbox = draw.textbbox((0, 0), tax_text, font=font_normal)
    draw.text((PAPER_WIDTH - MARGIN - bbox[2] + bbox[0], y_pos), tax_text, 
             fill=FG_COLOR, font=font_normal)
    y_pos += bbox[3] - bbox[1] + LINE_SPACING
    
    # Total (bold/larger)
    draw.text((MARGIN, y_pos), "TOTAL:", fill=FG_COLOR, font=font_large)
    total_text = format_price(total)
    bbox = draw.textbbox((0, 0), total_text, font=font_large)
    draw.text((PAPER_WIDTH - MARGIN - bbox[2] + bbox[0], y_pos), total_text, 
             fill=FG_COLOR, font=font_large)
    y_pos += bbox[3] - bbox[1] + LINE_SPACING * 2
    
    # Barcode section
    y_pos += draw_line(draw, y_pos)
    y_pos += LINE_SPACING * 2
    
    # Draw barcode
    barcode_width = PAPER_WIDTH - 2 * MARGIN
    barcode_img, barcode_pos = draw_barcode_placeholder(
        draw, MARGIN, y_pos, barcode_width, BAR_HEIGHT, BARCODE_DATA, BARCODE_TYPE
    )
    
    if barcode_img:
        # Paste actual barcode image
        img.paste(barcode_img, barcode_pos)
    
    y_pos += BAR_HEIGHT + LINE_SPACING
    
    # Barcode text
    y_pos += draw_centered_text(draw, y_pos, BARCODE_DATA, font_small)
    y_pos += LINE_SPACING * 2
    
    # Footer
    y_pos += draw_line(draw, y_pos)
    y_pos += LINE_SPACING * 2
    y_pos += draw_centered_text(draw, y_pos, FOOTER_TEXT, font_normal)
    y_pos += MARGIN
    
    # Crop to actual content
    img = img.crop((0, 0, PAPER_WIDTH, y_pos))
    
    return img

def main():
    """Main function to generate and save receipt preview"""
    print("🖨️  Generating receipt preview...")
    
    # Create receipt
    receipt_img = create_receipt()
    
    # Save to file
    receipt_img.save(OUTPUT_FILE)
    
    # Success message
    print(f"✅ Preview created: {OUTPUT_FILE}")
    print(f"📐 Dimensions: {receipt_img.width}x{receipt_img.height}px")
    print(f"📄 Paper width: 58mm ({PAPER_WIDTH}px at 203 dpi)")
    print("\n💡 Tip: Edit the configuration section at the top of this script and re-run to iterate!")
    
    # Try to open the image automatically (optional)
    try:
        import subprocess
        import sys
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", OUTPUT_FILE])
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", OUTPUT_FILE])
        elif sys.platform == "win32":
            subprocess.run(["start", OUTPUT_FILE], shell=True)
    except:
        pass  # Silently fail if we can't open the image

if __name__ == "__main__":
    main()
