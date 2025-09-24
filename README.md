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
| `PRINTER_CONSOLE_HOST`| Printer Console bind host               | `127.0.0.1`       |
| `PRINTER_CONSOLE_PORT`| Printer Console port (uncommon)         | `8765`            |
| `PRINTER_CONSOLE_DEBUG`| Enable Flask debug mode                | `false`           |

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

## 🖨️ Print Custom Text

Use the helper script to print arbitrary text.

Interactive (paste a single line, then press Enter):

```bash
python3 scripts/print_text.py
```

Pass text as CLI arguments:

```bash
python3 scripts/print_text.py "Hello world"
```

Pipe multi-line input:

```bash
printf "Line 1\nLine 2\n" | python3 scripts/print_text.py
```

Note (file transport → CUPS): If your `.env` uses a file-based printer (`THERMAL_PRINTER_TYPE=file` or `file_test`), the script writes ESC/POS to `PRINTER_FILE_PATH` and, when `CUPS_PRINTER` is set, auto-forwards it to CUPS using `lp -o raw` (same behavior as the daily brief).

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

---

## 🖥️ Printer Console (Always-On UI)

Run a local UI to trigger the daily brief and quick text prints.

Start the console:

```bash
python3 -m src.server_app
```

Environment variables:

- `PRINTER_CONSOLE_HOST`: default `127.0.0.1`
- `PRINTER_CONSOLE_PORT`: default `8765` (uncommon to avoid conflicts)
- `PRINTER_CONSOLE_DEBUG`: `true/false`

Then open `http://127.0.0.1:8765/` (or your configured host/port).

### Autostart on boot (systemd user service)

You can create a systemd user service to start the console on login/boot. Example unit:

```ini
[Unit]
Description=Receipt Printer Console
After=network-online.target

[Service]
Type=simple
Environment=PYTHONUNBUFFERED=1
Environment=PRINTER_CONSOLE_HOST=127.0.0.1
Environment=PRINTER_CONSOLE_PORT=8765
WorkingDirectory=%h/Documents/receipt-printer
ExecStart=%h/Documents/receipt-printer/venv/bin/python -m src.server_app
Restart=on-failure

[Install]
WantedBy=default.target
```

Save to `~/.config/systemd/user/receipt-printer-console.service`, then run:

```bash
systemctl --user daemon-reload
systemctl --user enable receipt-printer-console.service
systemctl --user start receipt-printer-console.service
systemctl --user status receipt-printer-console.service
```
