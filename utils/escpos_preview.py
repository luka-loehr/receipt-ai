#!/usr/bin/env python3
"""
ESC/POS Preview Tool
Converts ESC/POS commands to readable text for previewing without a printer
"""

import os
import sys

def preview_escpos_file(file_path):
    """Preview ESC/POS file by converting commands to readable text"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print("🖨️  ESC/POS Preview")
    print("=" * 50)
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Convert ESC/POS commands to readable text
        preview = convert_escpos_to_text(content)
        
        print(f"📁 File: {file_path}")
        print(f"📏 Size: {len(content)} bytes")
        print(f"📄 Preview (what the printer would output):")
        print("-" * 50)
        print(preview)
        print("-" * 50)
        
        # Save as readable text
        readable_file = file_path.replace('.txt', '_readable.txt')
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write(preview)
        
        print(f"💾 Readable version saved: {readable_file}")
        
        # Show character encoding analysis
        print(f"\n🔍 Character Analysis:")
        german_chars_found = any(b > 127 for b in content)
        print(f"   • German characters detected: {'Yes' if german_chars_found else 'No'}")
        print(f"   • Encoding: Likely Windows-1252 or similar")
        print(f"   • This preview shows what the printer will actually print")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def convert_escpos_to_text(escpos_data):
    """Convert ESC/POS binary data to readable text with proper German character handling"""
    # Common ESC/POS commands
    esc_commands = {
        b'\x1b\x40': '[INIT]',           # Initialize printer
        b'\x1b\x61\x00': '[ALIGN_LEFT]', # Align left
        b'\x1b\x61\x01': '[ALIGN_CENTER]', # Align center
        b'\x1b\x61\x02': '[ALIGN_RIGHT]', # Align right
        b'\x1b\x21\x00': '[FONT_NORMAL]', # Normal font
        b'\x1b\x21\x10': '[FONT_DOUBLE_HEIGHT]', # Double height
        b'\x1b\x21\x20': '[FONT_DOUBLE_WIDTH]', # Double width
        b'\x1b\x21\x30': '[FONT_DOUBLE]', # Double height + width
        b'\x1b\x2d\x00': '[BOLD_OFF]',    # Bold off
        b'\x1b\x2d\x01': '[BOLD_ON]',     # Bold on
        b'\x1b\x4a\x00': '[FEED]',        # Feed paper
        b'\x1b\x69': '[CUT]',             # Cut paper
        b'\x1b\x6d': '[PARTIAL_CUT]',     # Partial cut
        b'\x1b\x4d': '[FONT_A]',          # Font A
        b'\x1b\x52': '[INTERNATIONAL]',   # International charset
    }
    
    # Windows-1252 German character mapping (common in ESC/POS)
    german_chars = {
        0xf8: 'ü',  # ü
        0x81: 'ü',  # ü (alternative)
        0x8e: 'ä',  # ä
        0x94: 'ö',  # ö
        0x84: 'ä',  # ä (alternative)
        0x9a: 'Ü',  # Ü
        0x8a: 'Ü',  # Ü (alternative)
        0x9e: 'Ä',  # Ä
        0x99: 'Ö',  # Ö
        0x9f: 'ß',  # ß
    }
    
    # Convert to string, replacing control characters
    result = ""
    i = 0
    
    while i < len(escpos_data):
        byte = escpos_data[i:i+1]
        
        # Check for multi-byte commands
        found_command = False
        for cmd, desc in esc_commands.items():
            if escpos_data[i:i+len(cmd)] == cmd:
                result += desc
                i += len(cmd)
                found_command = True
                break
        
        if not found_command:
            # Check for single-byte commands
            if byte == b'\x0a':  # Line feed
                result += '\n'
            elif byte == b'\x0d':  # Carriage return
                result += '[CR]'
            elif byte == b'\x09':  # Tab
                result += '[TAB]'
            elif byte == b'\x1b':  # ESC
                result += '[ESC]'
            elif byte == b'\x00':  # Null
                result += '[NULL]'
            elif 32 <= ord(byte) <= 126:  # Printable ASCII
                result += byte.decode('ascii')
            else:
                # Handle extended characters (like German umlauts)
                char_code = ord(byte)
                if char_code in german_chars:
                    result += german_chars[char_code]
                else:
                    result += f'[{char_code:02x}]'  # Hex representation
            
            i += 1
    
    return result

def main():
    """Main function"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to the test print file
        file_path = "outputs/escpos/test_print.txt"
    
    preview_escpos_file(file_path)

if __name__ == "__main__":
    main()
