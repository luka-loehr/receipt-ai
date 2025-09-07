# Receipt Printer

🌍 **Multilingual AI daily briefings** for thermal printers. Fetches real data from Google APIs, generates culturally appropriate AI summaries in any language, and prints to ESC/POS thermal printers.

## Features

- **🌍 Universal Language Support**: AI-powered support for ANY language!
- **🤖 Complete AI Generation**: All content (greetings, dates, titles, briefs) is AI-generated and culturally appropriate
- **📊 Real Google data**: Gmail, Calendar, Tasks
- **🌤️ Weather integration** with OpenWeatherMap
- **🖨️ Thermal printer support** via ESC/POS protocol
- **📱 Multiple outputs**: PNG preview, text file, and direct printing
- **⚙️ Modular architecture** with easy language switching

## Quick Start

```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Place Google OAuth client credentials (Desktop App) JSON into cloud_credentials/ (any .json filename)
python3 oauth_setup.py
python3 printer_setup.py  # optional: configure USB thermal printer
python3 daily_brief.py
```

## 🌍 Language Configuration

Just set your language in the `.env` file:
```bash
RECEIPT_LANGUAGE=english
```

The AI can handle ANY language! Examples: `german`, `spanish`, `french`, `swahili`, `hindi`, `esperanto`, etc.

## What You Need

1. **Google Cloud credentials** (`google_credentials.json` placed at `cloud_credentials/google_credentials.json`)
   - Enable Gmail API, Calendar API, Tasks API
   - Download OAuth 2.0 credentials

2. **OpenAI API key** 
   - Get from https://platform.openai.com/api-keys

3. **OpenWeatherMap API key** (optional)
   - Get from https://openweathermap.org/api

4. **Thermal printer** (optional)
   - USB, Network, or Serial ESC/POS printer
   - Without printer: saves ESC/POS commands to file

## How It Works

1. **Setup**:
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `env.example` to `.env` and adjust values
   - Place Google OAuth client credentials JSON at `cloud_credentials/google_credentials.json`
   - Run OAuth: `python3 oauth_setup.py`
   - Setup printer (USB): `python3 printer_setup.py`

2. **Daily Brief** (`python3 daily_brief.py`):
   - Fetches emails, calendar, tasks, weather
   - Generates German AI summary
   - Creates PNG preview (384px wide, 58mm paper)
   - Saves text version
   - Prints to thermal printer via ESC/POS

## Files Generated

- `outputs/png/daily_brief.png` - Visual preview
- `outputs/txt/daily_brief.txt` - Plain text version  
- `outputs/escpos/test_print.txt` - Raw ESC/POS commands

## Thermal Printer Support

Supports USB, Network, and Serial ESC/POS printers:
- Auto-detects common thermal printer brands
- Handles German characters correctly
- 58mm paper width (384px at 203 DPI)
- File-based testing without hardware

## Configuration

Edit `USER_NAME` in `src/daily_brief.py` and environment variables in `.env`:

```bash
USER_NAME=Your Name
WEATHER_LOCATION=City,Country  
USER_TIMEZONE=Europe/Berlin
THERMAL_PRINTER_TYPE=usb_auto  # or network_auto, file_test
```

## Project Structure

```
receipt-printer/
├── daily_brief.py         # Main entry point
├── oauth_setup.py        # Google OAuth-only setup script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── src/                  # Core source code
│   ├── daily_brief.py    # Daily brief generation logic
│   ├── data_services.py  # Google APIs & weather integration
│   ├── thermal_printer.py# ESC/POS printer interface (reads config from .env)
│   └── printer_config.py # Printer configuration
├── utils/                # Utility scripts
│   └── escpos_preview.py # Preview ESC/POS files
├── outputs/              # Generated files
│   ├── png/             # PNG previews
│   ├── txt/             # Text versions
│   └── escpos/          # ESC/POS print files
└── cloud_credentials/    # Google API credentials
    └── google_credentials.json
```

## License

MIT