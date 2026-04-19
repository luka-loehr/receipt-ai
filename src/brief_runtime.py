#!/usr/bin/env python3
"""
Runtime helpers for saving, printing, and previewing the daily brief.
"""

import os
import subprocess
import sys
from typing import Optional

from .models import CompleteReceiptContent, PrintableContent
from .path_utils import ensure_parent_dir


def print_to_thermal_printer(receipt_content: CompleteReceiptContent, printable_content: PrintableContent) -> bool:
    """Print the daily brief using the configured thermal printer."""
    try:
        from .thermal_printer import ThermalPrinter

        printer = ThermalPrinter.from_env()
        if not printer.is_connected():
            print("❌ Could not connect to thermal printer")
            return False

        success = printer.print_daily_brief(receipt_content, printable_content)
        if success:
            print("✅ Daily brief printed successfully!")
        else:
            print("❌ Printing failed")
        printer.disconnect()
        return success
    except ImportError:
        print("⚠️  Thermal printer support not available. Install with: pip install python-escpos")
        return False
    except Exception as exc:
        print(f"❌ Thermal printer error: {exc}")
        return False


def build_text_brief_content(receipt_content: CompleteReceiptContent, printable_content: PrintableContent) -> str:
    """Build the plain-text receipt content that mirrors the PNG layout."""
    sections = [
        receipt_content.header.greeting,
        "",
        receipt_content.header.title,
        "",
        receipt_content.header.date_formatted,
        "",
        receipt_content.summary.brief,
    ]

    if receipt_content.task_section and printable_content.printable_tasks:
        sections.extend(["", receipt_content.task_section.section_title, ""])
        sections.extend(task.display_text for task in printable_content.printable_tasks)

    if receipt_content.shopping_section and printable_content.printable_shopping:
        sections.extend(["", receipt_content.shopping_section.section_title, ""])
        sections.extend(item.display_text for item in printable_content.printable_shopping)

    return "\n".join(sections) + "\n"


def save_text_brief(
    receipt_content: CompleteReceiptContent,
    printable_content: PrintableContent,
    output_txt_file: str,
) -> str:
    """Save the plain-text version of the daily brief."""
    content = build_text_brief_content(receipt_content, printable_content)
    ensure_parent_dir(output_txt_file)
    with open(output_txt_file, 'w', encoding='utf-8') as handle:
        handle.write(content)
    return output_txt_file


def submit_escpos_file_to_cups(printer_type: str, escpos_path: str, cups_printer: Optional[str]) -> None:
    """Submit the generated ESC/POS file to CUPS when configured."""
    if printer_type not in ('file', 'file_test') or not cups_printer or not os.path.exists(escpos_path):
        return

    try:
        completed = subprocess.run(
            ['lp', '-d', cups_printer, '-o', 'raw', escpos_path],
            check=True,
            capture_output=True,
            text=True,
        )
        message = completed.stdout.strip() or completed.stderr.strip()
        print(f"✅ Printed ({message})" if message else "✅ Printed")
    except subprocess.CalledProcessError as exc:
        error = exc.stderr.strip() if exc.stderr else str(exc)
        print(f"❌ Print failed: {error}")


def open_png_preview(image_path: str, enabled: bool) -> None:
    """Open the generated PNG preview when configured."""
    if not enabled:
        return

    try:
        if sys.platform == "darwin":
            subprocess.run(["open", image_path], check=False)
        elif sys.platform == "linux":
            for viewer in ["xdg-open", "display", "eog", "gthumb", "gimp"]:
                try:
                    subprocess.run([viewer, image_path], check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif sys.platform == "win32":
            subprocess.run(["start", image_path], shell=True, check=False)
    except Exception:
        pass
