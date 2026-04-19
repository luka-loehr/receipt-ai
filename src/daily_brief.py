#!/usr/bin/env python3
"""
Daily Brief Generator — Personalized Daily Summary Receipt.
Coordinates data loading, rendering, saving, and printing.
"""

import os

from .config import get_config
from .data_manager import ModularDataManager
from .path_utils import ensure_parent_dir
from .brief_rendering import render_daily_brief
from .brief_runtime import (
    open_png_preview,
    print_to_thermal_printer,
    save_text_brief,
    submit_escpos_file_to_cups,
)


config = get_config()


def create_daily_brief(data_manager: ModularDataManager):
    """Generate the daily briefing image and return reusable raw data."""
    receipt_content, raw_data = data_manager.generate_complete_receipt()
    _, _, _, raw_tasks, raw_shopping = raw_data

    printable_content = data_manager.format_for_printing(
        receipt_content,
        tasks=raw_tasks,
        shopping_items=raw_shopping,
    )
    save_text_brief(receipt_content, printable_content, config.output_txt_file)
    image = render_daily_brief(receipt_content, printable_content, raw_tasks)
    return image, receipt_content, printable_content, raw_data


def main():
    """Generate and save the daily briefing, then print to thermal printer."""
    print("📅  Generating your daily briefing...")
    current_config = get_config()
    print(f"✅ Language: {current_config.get_language_code()}")
    print()

    data_manager = ModularDataManager(current_config)
    brief_img, receipt_content, printable_content, raw_data = create_daily_brief(data_manager)

    ensure_parent_dir(config.output_png_file)
    brief_img.save(config.output_png_file)

    print("\n🖨️  Printing daily brief...")
    print_to_thermal_printer(receipt_content, printable_content)

    printer_type = os.getenv('THERMAL_PRINTER_TYPE', 'file_test').lower()
    cups_printer = os.getenv('CUPS_PRINTER')
    escpos_path = os.getenv('PRINTER_FILE_PATH', config.output_escpos_file)
    submit_escpos_file_to_cups(printer_type, escpos_path, cups_printer)

    preview_png = os.getenv('PREVIEW_PNG', 'true').lower() == 'true'
    open_png_preview(config.output_png_file, preview_png)

    return raw_data


if __name__ == "__main__":
    main()
