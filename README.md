# 🖨️ Receipt Printer - Smart Daily Briefings

A Python application that generates beautiful, thermal-printer-ready receipts with real-time data including weather, emails, calendar events, and AI-powered insights.

## ✨ Features

- **🌤️ Real-time Weather**: Current conditions, high/low temps, humidity, wind speed
- **📧 Smart Email Analysis**: AI-powered email prioritization and summarization
- **📅 Calendar Integration**: Today's meetings and events
- **🤖 AI Insights**: Gemini-powered daily motivation and insights
- **🖨️ Thermal Printer Ready**: Optimized for 58mm thermal printers (384px width)
- **🔄 Fallback System**: Gracefully degrades to mock data when APIs unavailable
- **🔒 Secure**: OAuth2 for Google services, no direct inbox access

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
python setup.py
```

This will guide you through configuring:
- OpenWeatherMap API key
- Google Gemini API key
- Gmail OAuth2 credentials
- Google Calendar OAuth2 credentials

### 3. Generate Receipts

```bash
# Generate morning briefing with real data
python morning_brief.py

# Generate standard receipt preview
python receipt_preview.py
```

## 🔑 API Setup

### OpenWeatherMap (Free)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your API key
3. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

### Google Gemini (Free Tier)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### Gmail & Calendar (OAuth2)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable APIs
3. Create OAuth2 credentials
4. Download as `gmail_credentials.json` and `calendar_credentials.json`

## 📁 File Structure

```
receipt-printer/
├── morning_brief.py          # Main morning briefing generator
├── receipt_preview.py        # Standard receipt generator
├── data_services.py          # Real-time data fetching
├── setup.py                  # Configuration helper
├── config.env.example        # Environment variables template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Use Cases

- **Morning Ritual**: Print daily briefing with coffee
- **Meeting Prep**: Quick overview of day's schedule
- **Email Triage**: Prioritized email summary
- **Weather Check**: Current conditions and forecast
- **Productivity Boost**: AI-generated daily insights

## 🔧 Configuration

Edit `.env` file to customize:

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

**Happy Printing! ☕📄**
