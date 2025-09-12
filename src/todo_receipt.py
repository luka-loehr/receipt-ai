#!/usr/bin/env python3
"""
Renderer for the standalone To-Do / Capture receipt.
This is independent from the daily brief.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import platform

from .config import get_config
from .todo_models import ToDoReceiptContent, TableSection


DPI_SCALE = 2
PAPER_WIDTH = 384 * DPI_SCALE
FINAL_WIDTH = 384
MARGIN = 8 * DPI_SCALE
BG_COLOR = "white"
FG_COLOR = "black"
GRAY_COLOR = "#666666"


def load_font(size=16):
    size = size * DPI_SCALE
    font_paths = []
    if os.name == 'nt':
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
        ]
    elif os.name == 'posix':
        if platform.system() == 'Darwin':
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, int(size))
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=int(size))
    except Exception:
        return ImageFont.load_default()


def draw_centered(draw, y, text, font, color=FG_COLOR):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (PAPER_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]


def draw_separator(draw, y, width=1):
    draw.line([(MARGIN, y), (PAPER_WIDTH - MARGIN, y)], fill=FG_COLOR, width=width)
    return width + 2


def _wrap_lines(draw, text, font, max_width):
    if not text:
        return []

    def measure(s: str) -> int:
        bb = draw.textbbox((0, 0), s, font=font)
        return bb[2] - bb[0]

    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word) if current else word
        if measure(candidate) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        if measure(word) > max_width:
            remaining = word
            while remaining:
                low, high = 1, len(remaining)
                best = 1
                while low <= high:
                    mid = (low + high) // 2
                    chunk = remaining[:mid] + ("-" if mid < len(remaining) else "")
                    if measure(chunk) <= max_width:
                        best = mid
                        low = mid + 1
                    else:
                        high = mid - 1
                chunk = remaining[:best]
                hyphenated = chunk + ("-" if best < len(remaining) else "")
                lines.append(hyphenated)
                remaining = remaining[best:]
        else:
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, font, max_width, color=FG_COLOR, spacing_mult=1.35):
    """Draw left-aligned wrapped text."""
    lines = _wrap_lines(draw, text, font, max_width)
    total_h = 0
    for ln in lines:
        draw.text((x, y), ln, fill=color, font=font)
        bb = draw.textbbox((0, 0), ln, font=font)
        line_h = bb[3] - bb[1]
        step = int(line_h * spacing_mult)
        y += step
        total_h += step
    return total_h


def draw_centered_wrapped(draw, y, text, font, max_width, color=FG_COLOR, spacing_mult=1.25):
    """Draw centered wrapped text within max_width."""
    lines = _wrap_lines(draw, text, font, max_width)
    total_h = 0
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=font)
        text_w = bb[2] - bb[0]
        x = (PAPER_WIDTH - text_w) // 2
        draw.text((x, y), ln, fill=color, font=font)
        line_h = bb[3] - bb[1]
        step = int(line_h * spacing_mult)
        y += step
        total_h += step
    return total_h


def draw_table(draw, y, table: TableSection, font_header, font_cell):
    left = MARGIN
    right = PAPER_WIDTH - MARGIN
    inner_width = right - left

    # Column widths: equal by default
    num_cols = max(1, len(table.columns))
    col_width = inner_width // num_cols

    # Optional title
    if table.title:
        y += draw_centered(draw, y, table.title, font_header, GRAY_COLOR)
        y += 6 * DPI_SCALE

    # Header background line
    y += draw_separator(draw, y, 1 * DPI_SCALE)

    # Header row
    x = left
    header_height = 0
    for col in table.columns:
        header_height = max(
            header_height,
            draw_wrapped(draw, x + 4 * DPI_SCALE, y + 4 * DPI_SCALE, col, font_header, col_width - 8 * DPI_SCALE)
        )
        x += col_width
    # Cell borders for header
    x = left
    for i in range(num_cols + 1):
        draw.line([(x, y), (x, y + header_height + 8 * DPI_SCALE)], fill=FG_COLOR, width=1)
        x += col_width
    draw.line([(left, y + header_height + 8 * DPI_SCALE), (right, y + header_height + 8 * DPI_SCALE)], fill=FG_COLOR, width=1)
    y += header_height + 10 * DPI_SCALE

    # Rows
    for row in table.rows:
        x = left
        row_height = 0
        for j in range(num_cols):
            cell_text = row[j] if j < len(row) else ""
            row_height = max(
                row_height,
                draw_wrapped(draw, x + 4 * DPI_SCALE, y + 4 * DPI_SCALE, cell_text, font_cell, col_width - 8 * DPI_SCALE)
            )
            x += col_width
        # vertical lines
        x = left
        for i in range(num_cols + 1):
            draw.line([(x, y), (x, y + row_height + 8 * DPI_SCALE)], fill=FG_COLOR, width=1)
            x += col_width
        # bottom line
        draw.line([(left, y + row_height + 8 * DPI_SCALE), (right, y + row_height + 8 * DPI_SCALE)], fill=FG_COLOR, width=1)
        y += row_height + 10 * DPI_SCALE

    return y


def render_todo_receipt(content: ToDoReceiptContent):
    img = Image.new("RGB", (PAPER_WIDTH, 1600 * DPI_SCALE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = load_font(26)
    font_normal = load_font(16)
    font_small = load_font(14)

    y = MARGIN

    # Header
    y += draw_separator(draw, y, 2 * DPI_SCALE)
    y += 10 * DPI_SCALE
    y += draw_centered_wrapped(draw, y, content.header.title, font_title, PAPER_WIDTH - 2 * MARGIN)
    y += 6 * DPI_SCALE
    y += draw_centered(draw, y, content.header.date_formatted, font_small)
    if content.header.source_label:
        y += 4 * DPI_SCALE
        y += draw_centered(draw, y, content.header.source_label, font_small)
    y += 12 * DPI_SCALE
    y += draw_separator(draw, y, 1 * DPI_SCALE)
    y += 16 * DPI_SCALE

    # Summary
    y += draw_wrapped(draw, MARGIN, y, content.summary.overview, font_normal, PAPER_WIDTH - 2 * MARGIN)
    if content.summary.key_points:
        y += 12 * DPI_SCALE
        for pt in content.summary.key_points[:6]:
            bullet = "• " + pt
            y += draw_wrapped(draw, MARGIN + 12 * DPI_SCALE, y, bullet, font_small, PAPER_WIDTH - 2 * MARGIN - 12 * DPI_SCALE)

    # To-Dos
    if content.todos:
        y += 14 * DPI_SCALE
        y += draw_separator(draw, y, 1 * DPI_SCALE)
        y += 10 * DPI_SCALE
        y += draw_centered(draw, y, "Action Items", font_small, GRAY_COLOR)
        y += 8 * DPI_SCALE
        for item in content.todos[:12]:
            box = "[ ]"
            line = f"{box} {item.title}"
            y += draw_wrapped(draw, MARGIN + 4 * DPI_SCALE, y, line, font_small, PAPER_WIDTH - 2 * MARGIN - 4 * DPI_SCALE)
            if item.notes:
                y += draw_wrapped(draw, MARGIN + 18 * DPI_SCALE, y, item.notes, font_small, PAPER_WIDTH - 2 * MARGIN - 18 * DPI_SCALE, color=GRAY_COLOR)
            y += 4 * DPI_SCALE

    # Attachments hint
    if content.attachments:
        y += 10 * DPI_SCALE
        y += draw_separator(draw, y, 1 * DPI_SCALE)
        y += 8 * DPI_SCALE
        y += draw_centered(draw, y, f"Attachments: {len(content.attachments)}", font_small, GRAY_COLOR)

    # Tables
    if content.tables:
        y += 12 * DPI_SCALE
        for tbl in content.tables:
            y = draw_table(draw, y, tbl, font_small, font_small)
            y += 8 * DPI_SCALE

    y += MARGIN
    img = img.crop((0, 0, PAPER_WIDTH, y))
    if DPI_SCALE > 1:
        img = img.resize((FINAL_WIDTH, int(y / DPI_SCALE)), Image.Resampling.LANCZOS)
    return img


def save_todo_receipt(content: ToDoReceiptContent):
    config = get_config()
    # Reuse base output folder; keep a separate filename
    out_dir = os.path.dirname(config.output_png_file)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "todo_capture.png")
    img = render_todo_receipt(content)
    img.save(out_path)
    return out_path


