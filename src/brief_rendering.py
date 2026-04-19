#!/usr/bin/env python3
"""
Rendering helpers for the daily brief PNG output.
"""

import os
import platform

from PIL import Image, ImageDraw, ImageFont

from .models import CompleteReceiptContent, PrintableContent, TaskData

# Using 2x resolution for better quality, then downscale
DPI_SCALE = 2
PAPER_WIDTH = 384 * DPI_SCALE
FINAL_WIDTH = 384
MARGIN = 8 * DPI_SCALE
BG_COLOR = "white"
FG_COLOR = "black"
GRAY_COLOR = "#666666"


def load_font(size: int = 16) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load fonts using a cross-platform fallback chain."""
    scaled_size = size * DPI_SCALE
    font_paths: list[str] = []

    if os.name == 'nt':
        font_paths = [
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simsun.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\calibri.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf",
        ]
    elif os.name == 'posix':
        if platform.system() == 'Darwin':
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Medium.ttc",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, int(scaled_size))
            except Exception:
                continue

    try:
        return ImageFont.load_default(size=int(scaled_size))
    except Exception:
        return ImageFont.load_default()


def draw_centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, color: str = FG_COLOR) -> int:
    """Draw centered text and return its height."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (PAPER_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font,
    max_width: int,
    color: str = FG_COLOR,
    line_spacing_multiplier: float = 1.4,
) -> int:
    """Draw wrapped text and return the total height used."""
    words = text.split()
    lines: list[str] = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = test_bbox[2] - test_bbox[0]

        if test_width <= max_width:
            current_line = test_line
        elif current_line:
            lines.append(current_line)
            current_line = word
        else:
            lines.append(word)

    if current_line:
        lines.append(current_line)

    total_height = 0
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        spacing = int(line_height * line_spacing_multiplier)
        y += spacing
        total_height += spacing

    return total_height


def draw_separator(draw: ImageDraw.ImageDraw, y: int, style: str = "solid", width: int = 1) -> int:
    """Draw a separator line and return the space used."""
    if style == "solid":
        draw.line([(MARGIN, y), (PAPER_WIDTH - MARGIN, y)], fill=FG_COLOR, width=width)
    elif style == "dashed":
        for x in range(MARGIN, PAPER_WIDTH - MARGIN, 8):
            draw.line([(x, y), (min(x + 4, PAPER_WIDTH - MARGIN), y)], fill=FG_COLOR, width=width)
    elif style == "dotted":
        for x in range(MARGIN, PAPER_WIDTH - MARGIN, 6):
            draw.ellipse([(x, y - 1), (x + 2, y + 1)], fill=FG_COLOR)
    return width + 2


def draw_decorative_border(draw: ImageDraw.ImageDraw, y: int, height: int = 3) -> int:
    """Draw a decorative border and return the used height."""
    for i in range(3):
        draw.line([(MARGIN, y + i), (PAPER_WIDTH - MARGIN, y + i)], fill=FG_COLOR, width=1)
    return height + 2


def render_daily_brief(
    receipt_content: CompleteReceiptContent,
    printable_content: PrintableContent,
    raw_tasks: list[TaskData],
) -> Image.Image:
    """Render the daily brief PNG image."""
    canvas_height = 1000 * DPI_SCALE
    img = Image.new("RGB", (PAPER_WIDTH, canvas_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = load_font(26)
    font_normal = load_font(16)
    font_small = load_font(14)
    font_tiny = load_font(12)

    y = MARGIN
    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    y += draw_centered_text(draw, y, receipt_content.header.greeting, font_title)
    y += 15 * DPI_SCALE
    y += draw_centered_text(draw, y, receipt_content.header.title, font_normal, GRAY_COLOR)
    y += 10 * DPI_SCALE
    y += draw_centered_text(draw, y, receipt_content.header.date_formatted, font_small)
    y += 20 * DPI_SCALE
    y += draw_separator(draw, y, "solid", 2 * DPI_SCALE)
    y += 25 * DPI_SCALE
    y += draw_wrapped_text(
        draw,
        MARGIN,
        y,
        receipt_content.summary.brief,
        font_normal,
        PAPER_WIDTH - MARGIN * 2,
        FG_COLOR,
        line_spacing_multiplier=1.4,
    )
    y += 25 * DPI_SCALE

    if receipt_content.task_section and printable_content.printable_tasks:
        y += draw_separator(draw, y, "dashed", 2)
        y += 15 * DPI_SCALE
        y += draw_centered_text(draw, y, receipt_content.task_section.section_title, font_small, GRAY_COLOR)
        y += 15 * DPI_SCALE

        for index, task in enumerate(printable_content.printable_tasks):
            checkbox_x = MARGIN + 10 * DPI_SCALE
            checkbox_size = 12 * DPI_SCALE
            draw.rectangle(
                [checkbox_x, y, checkbox_x + checkbox_size, y + checkbox_size],
                outline=FG_COLOR,
                width=1,
            )
            task_text = getattr(task, 'display_text', None) or raw_tasks[index].title
            draw.text((checkbox_x + checkbox_size + 8 * DPI_SCALE, y), task_text, fill=FG_COLOR, font=font_tiny)
            y += checkbox_size + 8 * DPI_SCALE
            if index < len(printable_content.printable_tasks) - 1:
                y += 5 * DPI_SCALE

        y += 15 * DPI_SCALE

    if receipt_content.shopping_section and printable_content.printable_shopping:
        y += draw_separator(draw, y, "dashed", 2)
        y += 15 * DPI_SCALE
        y += draw_centered_text(draw, y, receipt_content.shopping_section.section_title, font_small, GRAY_COLOR)
        y += 15 * DPI_SCALE

        for index, item in enumerate(printable_content.printable_shopping):
            checkbox_x = MARGIN + 10 * DPI_SCALE
            checkbox_size = 12 * DPI_SCALE
            draw.rectangle(
                [checkbox_x, y, checkbox_x + checkbox_size, y + checkbox_size],
                outline=FG_COLOR,
                width=1,
            )
            item_text = getattr(item, 'display_text', None) or item.original_title
            draw.text((checkbox_x + checkbox_size + 8 * DPI_SCALE, y), item_text, fill=FG_COLOR, font=font_tiny)
            y += checkbox_size + 8 * DPI_SCALE
            if index < len(printable_content.printable_shopping) - 1:
                y += 5 * DPI_SCALE

        y += 15 * DPI_SCALE

    y += draw_decorative_border(draw, y)
    y += 15 * DPI_SCALE
    y += MARGIN

    img = img.crop((0, 0, PAPER_WIDTH, y))
    if DPI_SCALE > 1:
        img = img.resize((FINAL_WIDTH, int(y / DPI_SCALE)), Image.Resampling.LANCZOS)
    return img
