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
# Clone the repository
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. One-Click Setup
```bash
# Run the complete setup script
python setup.py
```

**That's it!** The setup script will:
- ✅ Ask for your API keys (OpenWeatherMap, Gemini)
- ✅ Verify your `google_credentials.json` file
- ✅ Set up Google OAuth in your browser
- ✅ Generate Gmail and Calendar tokens
- ✅ Test everything works
- ✅ Make your app ready to use!

### 4. Generate Your First Brief
```bash
python morning_brief.py
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

1. **Google Cloud Console Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable Gmail + Calendar APIs
   - Create OAuth 2.0 credentials
   - Download as `google_credentials.json`

2. **API Keys**:
   - [OpenWeatherMap](https://openweathermap.org/api) (free tier)
   - [Google Gemini](https://makersuite.google.com/app/apikey)

3. **Environment Variables**:
   ```bash
   cp config.env.example .env
   # Edit .env with your API keys
   ```

## 📁 File Structure

```
receipt-printer/
├── setup.py                 # 🚀 Complete setup script
├── morning_brief.py         # Main morning briefing generator
├── data_services.py         # Real-time data fetching
├── config.env.example       # Environment variables template
├── requirements.txt          # Python dependencies
├── google_credentials.json  # Google OAuth credentials
└── README.md                # This file
```

## 🎯 Use Cases

- **Morning Ritual**: Print daily briefing with coffee
- **Meeting Prep**: Quick overview of day's schedule
- **Email Triage**: Prioritized email summary
- **Weather Check**: Current conditions and forecast
- **Productivity Boost**: AI-generated daily insights

## 🔧 Configuration

The setup script automatically creates and configures your `.env` file. You can customize:

```bash
# Location for weather
WEATHER_LOCATION=Berlin,DE

# User preferences
USER_NAME=YourName
USER_TIMEZONE=Europe/Berlin

# Email filtering
MAX_EMAILS_TO_PROCESS=10
EMAIL_PRIORITY_KEYWORDS=urgent,important,asap,deadline
EMAIL_SPAM_FILTERS=newsletter,marketing,promotion
```

## 🖨️ Printer Compatibility

- **Width**: 58mm thermal printers (384px at 203 DPI)
- **Format**: PNG output, optimized for thermal printing
- **Resolution**: High-quality rendering with proper scaling

## 🛡️ Security Features

- **No Direct Access**: Uses official APIs with proper OAuth2
- **Local Processing**: All data processing happens locally
- **Configurable Filters**: Spam and priority filtering
- **Fallback Mode**: Works offline with mock data

## 🚨 Troubleshooting

### Common Issues

1. **"No API key found"**: Run `python setup.py` to configure
2. **Font loading errors**: Script will fall back to system fonts
3. **Image won't open**: Install an image viewer or use `xdg-open`
4. **Permission errors**: Check file permissions and virtual environment

### Debug Mode

```bash
# Test data services
python data_services.py

# Check configuration
python setup.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify for your needs.

## 🙏 Acknowledgments

- OpenWeatherMap for weather data
- Google Gemini for AI insights
- Google APIs for email and calendar
- PIL/Pillow for image generation
- Python community for excellent libraries

---

**Need help?** The `python setup.py` script handles everything automatically! 🚀
