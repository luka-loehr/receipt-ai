# 🧾 Receipt Printer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)
[![Thermal Printer](https://img.shields.io/badge/ESC--POS-compatible-lightgrey.svg)](#)

**AI-powered daily briefings — printed to your thermal receipt printer.**

Generate multilingual summaries from your Gmail, Calendar, Tasks, and weather data. Everything is personalized, culturally adapted, and printed using ESC/POS printers.

---

## ✨ Features

- 🌐 **Multilingual AI** — Any language, culture-aware formatting
- 📬 **Google Integration** — Gmail, Calendar, Tasks
- ☀️ **Weather Data** — OpenWeatherMap integration
- 🖨️ **ESC/POS Support** — USB, network, or file-based printing
- 🖼️ **Multiple Outputs** — PNG preview, plain text, ESC/POS commands
- ⚙️ **Fully Configurable** — Easy .env setup

---

## 🚀 Quick Start

```bash
git clone https://github.com/luka-loehr/receipt-printer.git
cd receipt-printer
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
```

1. Fill in `.env` with your API keys & preferences
2. Setup Google Cloud: enable Gmail, Calendar, Tasks API + OAuth creds  
3. Place OAuth JSON file into `cloud_credentials/`
4. Run initial auth:  
   ```bash
   python3 oauth_setup.py
   ```
5. (Optional) Setup USB printer:  
   ```bash
   python3 printer_setup.py
   ```
6. Generate your daily briefing:  
   ```bash
   python3 daily_brief.py
   ```

---

## ⚙️ Configuration

| Variable              | Description                             | Default           |
|----------------------|-----------------------------------------|-------------------|
| `USER_NAME`          | Personalization                         | `Luka`            |
| `RECEIPT_LANGUAGE`   | AI response language                    | `german`          |
| `USER_TIMEZONE`      | Your timezone                          | `Europe/Berlin`   |
| `WEATHER_LOCATION`   | Weather city & country                 | `Karlsruhe,DE`    |
| `THERMAL_PRINTER_TYPE`| `usb`, `network`, or `file_test`       | `file_test`       |
| `PREVIEW_PNG`        | Auto-open preview                      | `true`            |

---

## 🗂️ Project Structure

```txt
receipt-printer/
├── daily_brief.py         # Main script
├── oauth_setup.py         # Google OAuth flow
├── printer_setup.py       # USB printer config
├── src/
│   ├── daily_brief.py     # Summary generation
│   ├── data_services.py   # Gmail, Calendar, Weather
│   ├── thermal_printer.py # ESC/POS logic
│   └── ...
├── outputs/               # PNG, TXT, ESC/POS files
├── cloud_credentials/     # OAuth JSON file
```

---

## 🧪 Requirements

- ✅ Python 3.8+
- ✅ OpenAI API key  
- 🔄 Google Cloud Project (OAuth2 + APIs enabled)  
- 🌦️ OpenWeatherMap API (optional)  
- 🖨️ Any ESC/POS-compatible thermal printer (USB, network)

---

## 🛠 Troubleshooting

- **No printer found**: Try `printer_setup.py` and check USB power
- **OAuth fails**: Recheck `.json` in `cloud_credentials/` and enabled APIs
- **Empty output**: Validate your OpenAI key and internet connection

---

## 🤝 Contributing

```bash
# 1. Fork & clone the repo
# 2. Create a new feature branch
# 3. Make and test your changes
# 4. Submit a PR 🙌
```

---

## 📄 License

MIT License — see [`LICENSE`](LICENSE) file.

---

## 💬 Support & Feedback

- [GitHub Issues](https://github.com/luka-loehr/receipt-printer/issues)
- [Discussions](https://github.com/luka-loehr/receipt-printer/discussions)
