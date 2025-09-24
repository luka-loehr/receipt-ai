#!/usr/bin/env python3
import os
import threading
import subprocess
from typing import Optional
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

app = Flask(__name__)


def run_daily_brief_blocking() -> tuple[bool, str]:
    """Run the daily brief script synchronously in a subprocess."""
    try:
        cp = subprocess.run([
            os.getenv('PYTHON_BIN', 'python3'),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'daily_brief.py'))
        ], capture_output=True, text=True)
        success = cp.returncode == 0
        output = (cp.stdout or '') + (cp.stderr or '')
        return success, output
    except Exception as e:
        return False, str(e)


def print_text_blocking(text: str) -> tuple[bool, str]:
    """Run the print_text script synchronously in a subprocess."""
    try:
        cp = subprocess.run([
            os.getenv('PYTHON_BIN', 'python3'),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'print_text.py')),
            text
        ], capture_output=True, text=True)
        success = cp.returncode == 0
        output = (cp.stdout or '') + (cp.stderr or '')
        return success, output
    except Exception as e:
        return False, str(e)


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Printer Console</title>
  <style>
    :root {
      --bg: #0b1220; --panel: #121a2b; --text: #e7eefc; --muted:#9bb3d3; --accent:#4f8cff; --accent2:#4fe3c1; --danger:#ff6b6b;
    }
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Noto Sans", "Helvetica Neue", Arial; background: var(--bg); color: var(--text); }
    .container { max-width: 900px; margin: 0 auto; padding: 24px; }
    .header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 24px; }
    .title { font-size: 20px; font-weight: 700; letter-spacing: 0.3px; }
    .status { font-size: 13px; color: var(--muted); }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card { background: linear-gradient(180deg, #141e31 0%, #0f1727 100%); border: 1px solid #20304f; border-radius: 12px; padding: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .card h3 { margin: 0 0 10px; font-size: 16px; }
    .btn { appearance:none; border:none; background: linear-gradient(135deg, var(--accent), var(--accent2)); color:#071121; font-weight:700; padding: 10px 14px; border-radius: 10px; cursor:pointer; transition: transform .06s ease, filter .2s ease; }
    .btn:hover { filter: brightness(1.05); }
    .btn:active { transform: translateY(1px); }
    .btn--secondary { background: transparent; color: var(--text); border: 1px solid #2a3e60; }
    .input { width: 100%; background: #0c1322; border: 1px solid #20304f; color: var(--text); padding: 10px 12px; border-radius: 10px; outline: none; font-size: 14px; }
    .input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(79,140,255,.15); }
    .row { display:flex; gap: 10px; align-items:center; }
    .log { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; color: var(--muted); white-space: pre-wrap; background:#0b1220; border:1px dashed #2a3e60; padding: 10px; border-radius: 10px; max-height: 240px; overflow:auto; }
    @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
  </style>
  <script>
    async function runDailyBrief() {
      setStatus('daily', 'loading');
      const res = await fetch('/api/daily-brief', { method: 'POST' });
      const data = await res.json();
      setStatus('daily', data.success ? 'done' : 'error');
      setLog('daily', data.output || (data.success ? 'Done' : 'Failed'));
    }
    async function printText() {
      const text = document.getElementById('printText').value || '';
      if (!text.trim()) { alert('Please enter text to print'); return; }
      setStatus('text', 'loading');
      const res = await fetch('/api/print-text', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
      const data = await res.json();
      setStatus('text', data.success ? 'done' : 'error');
      setLog('text', data.output || (data.success ? 'Printed' : 'Failed'));
    }
    function setStatus(kind, state) {
      const el = document.getElementById(kind + 'Status');
      if (!el) return;
      el.textContent = state === 'loading' ? 'Loading…' : state === 'done' ? 'Done' : state === 'error' ? 'Error' : '';
    }
    function setLog(kind, text) {
      const el = document.getElementById(kind + 'Log');
      if (!el) return;
      el.textContent = text || '';
    }
  </script>
  <link rel="icon" href="data:," />
  <meta http-equiv="Cache-Control" content="no-store" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <meta name="color-scheme" content="dark light">
  <meta name="theme-color" content="#0b1220">
  <meta name="description" content="Always-on Printer Console for daily briefs and quick prints" />
  <style>/* prevent FOUC */</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title">🖨️ Printer Console</div>
      <div class="status">Always-on UI</div>
    </div>
    <div class="grid">
      <div class="card">
        <h3>Daily Brief</h3>
        <div class="row">
          <button class="btn" onclick="runDailyBrief()">Run & Print</button>
          <span id="dailyStatus" class="status"></span>
        </div>
        <div id="dailyLog" class="log" style="margin-top:10px"></div>
      </div>
      <div class="card">
        <h3>Quick Text Print</h3>
        <div class="row" style="margin-bottom:10px">
          <input id="printText" class="input" placeholder="Enter text to print" />
          <button class="btn" onclick="printText()">Print</button>
        </div>
        <div id="textLog" class="log"></div>
        <div style="margin-top:8px; font-size:12px; color: var(--muted)">Uses the same file/CUPS flow as daily brief if configured.</div>
      </div>
    </div>
  </div>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.post("/api/daily-brief")
def api_daily_brief():
    success, output = run_daily_brief_blocking()
    return jsonify({"success": success, "output": output})


@app.post("/api/print-text")
def api_print_text():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text') or '').strip()
    if not text:
        return jsonify({"success": False, "output": "No text provided"}), 400
    success, output = print_text_blocking(text)
    return jsonify({"success": success, "output": output})


def run():
    host = os.getenv('PRINTER_CONSOLE_HOST', '127.0.0.1')
    # uncommon default port to avoid conflicts
    port = int(os.getenv('PRINTER_CONSOLE_PORT', '8765'))
    debug = os.getenv('PRINTER_CONSOLE_DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run()


