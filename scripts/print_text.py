#!/usr/bin/env python3
import sys

def _read_text_from_input() -> str:
    """
    Determine the text to print using the following priority:
    1) If there are CLI args, join them with spaces.
    2) If stdin is piped (not a TTY), read all from stdin.
    3) Otherwise, prompt for a single line and return it.
    """
    import sys as _sys
    import os as _os

    # 1) CLI args provided
    if len(_sys.argv) > 1:
        return " ".join(_sys.argv[1:])

    # 2) Piped input
    try:
        if not _sys.stdin.isatty():
            return _sys.stdin.read()
    except Exception:
        pass

    # 3) Interactive single-line prompt
    try:
        return input("Paste text and press Enter to print: ")
    except EOFError:
        return ""


def main():
    # Ensure project root is on sys.path
    import os
    root = os.path.dirname(os.path.dirname(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    from src.thermal_printer import ThermalPrinter

    text = _read_text_from_input()
    if not text:
        print("⚠️ No text provided; nothing to print.")
        sys.exit(0)

    printer = ThermalPrinter.from_env()
    if not printer.is_connected():
        print("❌ Could not connect to thermal printer")
        sys.exit(1)

    ok = printer.print_plain_text(text)

    # If using file-based transport, optionally forward to CUPS
    try:
        import os
        import subprocess
        if ok and getattr(printer, 'config', None) and printer.config.connection_type == 'file':
            cups_printer = os.getenv('CUPS_PRINTER')
            escpos_path = os.getenv('PRINTER_FILE_PATH', printer.config.device_id)
            if cups_printer and escpos_path and os.path.exists(escpos_path):
                try:
                    cp = subprocess.run(['lp', '-d', cups_printer, '-o', 'raw', escpos_path], check=True, capture_output=True, text=True)
                    msg = (cp.stdout or cp.stderr).strip()
                    if msg:
                        print(f"✅ Sent to CUPS: {msg}")
                except subprocess.CalledProcessError as e:
                    err = (e.stderr or str(e)).strip()
                    print(f"❌ CUPS print failed: {err}")
    except Exception:
        pass

    printer.disconnect()
    if not ok:
        sys.exit(2)
    print("✅ Text printed")

if __name__ == "__main__":
    main()


