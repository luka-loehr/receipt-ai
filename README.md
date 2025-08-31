# 🧾 Receipt Printer

Personalized German morning briefs for thermal printers with real-time Google data.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Setup](https://img.shields.io/badge/Setup-One%20Script-orange?style=flat)](setup.py)

Generate beautiful, personalized morning briefings with real-time data from Google Calendar, Gmail, and weather services. Perfect for your morning coffee ritual! ☕

## Features

- **🇩🇪 German Localization**: Complete German interface and AI insights
- **📅 Real Calendar Data**: Live Google Calendar integration  
- **📧 Live Email Data**: Real-time Gmail processing with AI analysis
- **🌤️ Weather Integration**: Current conditions and forecasts
- **🤖 AI-Powered Insights**: Gemini AI generates personalized daily insights
- **🖨️ Thermal Printer Ready**: Optimized for 58mm thermal printers
- **🔐 Unified Google Auth**: Single credentials file for all Google services

## Quick Start

```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python setup.py
python morning_brief.py
```

## Setup

The `setup.py` script automatically:
- ✅ Configures API keys (OpenWeatherMap, Gemini)
- ✅ Verifies your `google_credentials.json` file
- ✅ Sets up Google OAuth in your browser
- ✅ Generates Gmail and Calendar tokens
- ✅ Tests everything works

## License

MIT License – Personal project

## Support

- Issues: https://github.com/luka-loehr/receipt-printer/issues
- Questions: contact@lukaloehr.de

---

Developed by [Luka Löhr](https://github.com/luka-loehr) for personalized morning productivity.
