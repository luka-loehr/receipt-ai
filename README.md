# 🧾 Receipt Printer

**Personalized German Morning Briefs for Thermal Printers**

Generate beautiful, personalized morning briefings with real-time data from Google Calendar, Gmail, and weather services. Perfect for your morning coffee ritual! ☕

## ✨ Features

- **🇩🇪 German Localization**: Complete German interface and AI insights
- **📅 Real Calendar Data**: Live Google Calendar integration
- **📧 Live Email Data**: Real-time Gmail processing with AI analysis
- **🌤️ Weather Integration**: Current conditions and forecasts
- **🤖 AI-Powered Insights**: Gemini AI generates personalized daily insights
- **🖨️ Thermal Printer Ready**: Optimized for 58mm thermal printers
- **🔐 Unified Google Auth**: Single credentials file for all Google services

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- `google_credentials.json` from Google Cloud Console
- Virtual environment (recommended)

### 2. Installation
```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup & Run
```bash
# Complete setup in one command
python setup.py

# Generate your morning brief
python morning_brief.py
```

## 🔧 Setup Process

The `setup.py` script automatically:
- ✅ Configures API keys (OpenWeatherMap, Gemini)
- ✅ Verifies your `google_credentials.json` file
- ✅ Sets up Google OAuth in your browser
- ✅ Generates Gmail and Calendar tokens
- ✅ Tests everything works
- ✅ Makes your app ready to use!

## 📁 Files

```
receipt-printer/
├── setup.py                 # 🚀 Complete setup script
├── morning_brief.py         # Main morning briefing generator
├── data_services.py         # Real-time data fetching
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🎯 What You Get

- **Morning Ritual**: Print daily briefing with coffee
- **Meeting Prep**: Quick overview of day's schedule
- **Email Triage**: Prioritized email summary
- **Weather Check**: Current conditions and forecast
- **Productivity Boost**: AI-generated daily insights

## 🖨️ Printer Compatibility

- **Width**: 58mm thermal printers (384px at 203 DPI)
- **Format**: PNG output, optimized for thermal printing
- **Resolution**: High-quality rendering with proper scaling

---

**That's it!** Just run `python setup.py` and you're ready to go! 🚀
