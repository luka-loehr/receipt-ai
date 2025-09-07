# Receipt Printer

🌍 **AI-Powered Daily Briefings for Thermal Printers**

Generate personalized, multilingual daily summaries that print directly to ESC/POS thermal printers. Fetches real data from Google APIs (Gmail, Calendar, Tasks), weather, and uses AI to create culturally appropriate briefings in any language.

## What This Is

This project creates beautiful, receipt-style daily briefings that print on thermal printers. Perfect for:

- **Daily productivity**: Get a physical summary of your day
- **Multilingual support**: Works in any language (German, English, Spanish, etc.)
- **Real data integration**: Your actual emails, calendar, tasks, and weather
- **Thermal printer compatibility**: Works with any ESC/POS printer (USB, Network, Serial)
- **AI-powered content**: Intelligent summaries and culturally appropriate formatting

## Features

- 🌍 **Universal Language Support**: AI handles any language automatically
- 🤖 **Complete AI Generation**: All content is AI-generated and culturally appropriate
- 📊 **Real Google Data**: Gmail, Calendar, Tasks integration
- 🌤️ **Weather Integration**: OpenWeatherMap weather data
- 🖨️ **Thermal Printer Support**: USB, Network, Serial ESC/POS printers
- 📱 **Multiple Outputs**: PNG preview, text file, and direct printing
- ⚙️ **Modular Architecture**: Easy configuration and language switching

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env
```

Edit `.env` and fill in your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional: Customize your settings
USER_NAME=Your Name
RECEIPT_LANGUAGE=english  # or german, spanish, french, etc.
WEATHER_LOCATION=Your City,Country
```

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
   - Google Tasks API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download the JSON file
6. Place it in `cloud_credentials/` folder (any filename ending in `.json`)

### 4. Authorize Google APIs

```bash
python3 oauth_setup.py
```

This will open your browser for Google authorization and save tokens for all Google services.

### 5. Setup Thermal Printer (Optional)

If you have a thermal printer:

```bash
python3 printer_setup.py
```

This scans USB devices and configures your printer automatically.

### 6. Generate Daily Brief

```bash
python3 daily_brief.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USER_NAME` | Your name for personalization | `Luka` |
| `RECEIPT_LANGUAGE` | Language for AI content | `german` |
| `USER_TIMEZONE` | Your timezone | `Europe/Berlin` |
| `WEATHER_LOCATION` | Weather location | `Karlsruhe,DE` |
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENWEATHER_API_KEY` | Weather API key (optional) | - |
| `THERMAL_PRINTER_TYPE` | Printer type: `usb`, `network`, `file_test` | `file_test` |
| `PREVIEW_PNG` | Auto-open PNG preview | `true` |

### Printer Types

- **`file_test`**: Saves ESC/POS commands to file (default, no hardware needed)
- **`usb`**: USB thermal printer (configured via `printer_setup.py`)
- **`network`**: Network printer (set `PRINTER_HOST` and `PRINTER_PORT`)

## What You Need

### Required
- **Python 3.8+**
- **OpenAI API key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### Optional
- **OpenWeatherMap API key**: Get from [OpenWeatherMap](https://openweathermap.org/api)
- **Thermal printer**: Any ESC/POS compatible printer (USB, Network, or Serial)

## How It Works

1. **Data Collection**: Fetches emails, calendar events, tasks, and weather
2. **AI Processing**: Uses OpenAI to generate culturally appropriate summaries
3. **Content Generation**: Creates structured receipt content with tasks and shopping lists
4. **Output Creation**: Generates PNG preview, text file, and ESC/POS print commands
5. **Printing**: Sends commands to thermal printer or saves to file

## Generated Files

- `outputs/png/daily_brief.png` - Visual preview
- `outputs/txt/daily_brief.txt` - Plain text version
- `outputs/escpos/daily_brief.txt` - ESC/POS print commands

## Project Structure

```
receipt-printer/
├── daily_brief.py         # Main entry point
├── oauth_setup.py         # Google OAuth setup
├── printer_setup.py       # USB printer configuration
├── env.example            # Environment template
├── requirements.txt       # Python dependencies
├── src/                   # Core source code
│   ├── daily_brief.py     # Daily brief generation
│   ├── data_services.py   # Google APIs & weather
│   ├── thermal_printer.py # ESC/POS printer interface
│   ├── config.py          # Configuration management
│   └── models.py          # Data models
├── outputs/               # Generated files
│   ├── png/              # PNG previews
│   ├── txt/              # Text versions
│   └── escpos/           # ESC/POS print files
└── cloud_credentials/     # Google API credentials
    └── *.json            # OAuth client files
```

## Troubleshooting

### No USB devices found
- Ensure printer is connected and powered on
- Install pyusb: `pip install pyusb`
- Try network printer instead

### Google OAuth fails
- Check that JSON file is in `cloud_credentials/` folder
- Verify APIs are enabled in Google Cloud Console
- Delete `token_autogenerated/` folder and retry

### AI content not generating
- Verify OpenAI API key is correct
- Check internet connection
- Ensure API key has sufficient credits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: [GitHub Issues](https://github.com/luka-loehr/receipt-printer/issues)
- Discussions: [GitHub Discussions](https://github.com/luka-loehr/receipt-printer/discussions)