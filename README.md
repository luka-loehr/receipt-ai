# receipt-ai — Daily briefing printer for thermal receipt printers

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat)](LICENSE)

**receipt-ai** is a Python script that pulls data from Gmail, Google Calendar, Google Tasks, and OpenWeatherMap, generates a daily summary via OpenAI, and prints it to an ESC/POS thermal receipt printer. Supports USB, network, and file-based printer transports. Output can also be saved as PNG or plain text.

---

## Features

- **Data aggregation** — fetches emails, calendar events, tasks, and weather from Google APIs and OpenWeatherMap
- **Summary generation** — OpenAI generates a condensed daily briefing; language and formatting are configurable
- **ESC/POS printing** — sends formatted output to USB, network, or file-based thermal printers
- **PNG preview** — renders the receipt as an image before printing
- **Printer console** — local web UI (Flask) to trigger prints and send custom text
- **Systemd service** — autostart support for always-on console

---

## Quick Start

```bash
git clone https://github.com/luka-loehr/receipt-ai.git
cd receipt-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

1. Fill in `.env` with API keys and printer config
2. Enable Gmail, Calendar, and Tasks APIs in Google Cloud Console; add OAuth credentials
3. Place the OAuth JSON in `cloud_credentials/`
4. Run initial auth: `python3 oauth_setup.py`
5. (Optional) Configure USB printer: `python3 printer_setup.py`
6. Generate briefing: `python3 daily_brief.py`

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `USER_NAME` | Name used in briefing | `Luka` |
| `RECEIPT_LANGUAGE` | Briefing language | `german` |
| `USER_TIMEZONE` | Timezone | `Europe/Berlin` |
| `WEATHER_LOCATION` | City and country code | `Karlsruhe,DE` |
| `THERMAL_PRINTER_TYPE` | `usb`, `network`, or `file_test` | `file_test` |
| `PREVIEW_PNG` | Auto-open PNG preview | `true` |

---

## Printer Console

Run a local web UI at `http://127.0.0.1:8765/` to trigger briefings and print custom text:

```bash
python3 -m src.server_app
```

For systemd autostart, see the example unit file in the docs.

---

## License

[MIT](LICENSE)

---

## Support

- [Report bugs](https://github.com/luka-loehr/receipt-ai/issues)
- [luka@lukaloehr.com](mailto:luka@lukaloehr.com)

---

Developed by [Luka Löhr](https://github.com/luka-loehr)
