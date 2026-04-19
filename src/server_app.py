#!/usr/bin/env python3
"""
Flask web console for generating the daily brief, printing quick text,
and creating capture receipts from pasted text or uploaded images.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file

from .capture_ai import CaptureAI
from .config import get_config
from .path_utils import PROJECT_ROOT, path_to_file_url
from .todo_receipt import save_todo_receipt


load_dotenv(PROJECT_ROOT / ".env")

app = Flask(__name__, template_folder=str(PROJECT_ROOT / "src" / "templates"))


def _run_subprocess(args: list[str]) -> tuple[bool, str]:
    """Run a command inside the project root and return status plus output."""
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
    except Exception as exc:
        return False, str(exc)

    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode == 0, output


def run_daily_brief_blocking() -> tuple[bool, str]:
    """Run the daily brief script synchronously in a subprocess."""
    return _run_subprocess([sys.executable, str(PROJECT_ROOT / "daily_brief.py")])


def print_text_blocking(text: str) -> tuple[bool, str]:
    """Run the print_text script synchronously in a subprocess."""
    return _run_subprocess([sys.executable, str(PROJECT_ROOT / "scripts" / "print_text.py"), text])


def get_capture_output_path() -> Path:
    """Return the PNG path used for capture receipts."""
    output_dir = Path(get_config().output_png_file).resolve().parent
    return output_dir / "todo_capture.png"


def generate_capture_receipt(text: str, image_path: Path | None) -> Path:
    """Generate a capture receipt directly inside the Flask process."""
    image_url = path_to_file_url(str(image_path)) if image_path else None
    content = CaptureAI().analyze(text or None, image_url)
    return Path(save_todo_receipt(content)).resolve()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/capture")
def capture():
    return render_template("capture.html")


@app.post("/api/daily-brief")
def api_daily_brief():
    success, output = run_daily_brief_blocking()
    return jsonify({"success": success, "output": output})


@app.post("/api/print-text")
def api_print_text():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text") or "").strip()
    if not text:
        return jsonify({"success": False, "output": "No text provided"}), 400

    success, output = print_text_blocking(text)
    return jsonify({"success": success, "output": output})


@app.post("/api/capture")
def api_capture():
    text = str(request.form.get("text") or "").strip()
    upload = request.files.get("image")
    if not text and (upload is None or not upload.filename):
        return jsonify({"success": False, "output": "Provide text or an image"}), 400

    temp_path: Path | None = None
    try:
        if upload is not None and upload.filename:
            suffix = Path(upload.filename).suffix or ".upload"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                upload.save(temp_file.name)
                temp_path = Path(temp_file.name)

        output_path = generate_capture_receipt(text, temp_path)
        if not output_path.exists():
            return jsonify({"success": False, "output": "Capture PNG was not created"}), 500

        return jsonify({"success": True, "path": f"/api/capture/image?ts={int(output_path.stat().st_mtime)}"})
    except Exception as exc:
        return jsonify({"success": False, "output": str(exc)}), 500
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


@app.get("/api/capture/image")
def api_capture_image():
    output_path = get_capture_output_path()
    if not output_path.exists():
        return jsonify({"success": False, "output": "No capture PNG available"}), 404
    return send_file(output_path)


def run():
    host = os.getenv("PRINTER_CONSOLE_HOST", "127.0.0.1")
    port = int(os.getenv("PRINTER_CONSOLE_PORT", "8765"))
    debug = os.getenv("PRINTER_CONSOLE_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run()
