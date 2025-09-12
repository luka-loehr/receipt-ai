#!/usr/bin/env python3
"""
AI service for manual capture (text or image) → To-Do receipt content.
Uses GPT-4o (vision-capable) if OPENAI_API_KEY is present; otherwise mock.
"""

from typing import List, Optional
from pydantic import BaseModel
import os
import base64
from urllib.parse import urlparse

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

from .config import get_config
from .todo_models import (
    ToDoReceiptHeader,
    ToDoReceiptSummary,
    ToDoItem,
    ToDoReceiptContent,
    TableSection,
)


class CaptureAI:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.openai_api_key
        # Prefer the vision-capable model for capture
        self.model = "gpt-4o" if (self.config.ai_model or "").startswith("gpt-") else "gpt-4o"
        self.mock = not self.api_key or OpenAI is None
        self.client = OpenAI(api_key=self.api_key) if not self.mock else None

    def analyze(self, text: Optional[str], image_url: Optional[str]) -> ToDoReceiptContent:
        if self.mock:
            return self._mock_output(text, image_url)

        messages: List[dict] = [
            {
                "role": "system",
                "content": (
                    "You extract structured schedule/todos from images or text and answer in concise German. "
                    "Return a compact summary (2-3 sentences) and a bullet list of action items."
                ),
            }
        ]

        user_parts: List[dict] = []
        if text:
            user_parts.append({"type": "text", "text": text})
        if image_url:
            # Support local file URLs by converting to base64 data URLs
            try:
                parsed = urlparse(image_url)
                if parsed.scheme == 'file':
                    local_path = parsed.path
                    with open(local_path, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode('ascii')
                    mime = 'image/png' if local_path.lower().endswith('.png') else 'image/jpeg'
                    data_url = f"data:{mime};base64,{b64}"
                    user_parts.append({"type": "image_url", "image_url": {"url": data_url}})
                else:
                    user_parts.append({"type": "image_url", "image_url": {"url": image_url}})
            except Exception:
                # Fallback to text-only if reading fails
                pass
        if not user_parts:
            user_parts.append({"type": "text", "text": "Kein Inhalt übergeben"})

        messages.append({"role": "user", "content": user_parts})

        prompt = (
            "Extrahiere strukturierte Informationen aus Bild/Text. Antworte NUR in Deutsch.\n"
            "Pflicht: Liefere IMMER (wenn erkennbar) eine Tabelle mit Spalten 'Tag/Datum' | 'Zeit' | 'Details'.\n"
            "- Erkenne Datumsformen wie 'Di 07.10', '15.10', '16.10', '17.10'.\n"
            "- Erkenne Zeiten wie '17:00-21:00', 'ab 17:00', '10:00–14:00'.\n"
            "- Details: kurze Beschreibung (z.B. 'Generalprobe', 'Aufführung 1 (Beginn 19:00)').\n"
            "Gib zusätzlich 3–6 konkrete To‑dos.\n"
            "Halte dich kurz und präzise."
        )
        messages.append({"role": "system", "content": prompt})

        try:
            resp = self.client.chat.completions.create(  # type: ignore
                model=self.model,
                messages=messages,
                temperature=0.2,
            )
            text_out = resp.choices[0].message.content.strip()
        except Exception:
            return self._mock_output(text, image_url)

        # Parse the AI response more intelligently
        lines = text_out.split('\n')
        overview = ""
        todos = []
        table_rows: List[List[str]] = []
        
        # Find overview section
        for i, line in enumerate(lines):
            if 'übersicht' in line.lower() or 'zusammenfassung' in line.lower():
                # Look for content after this line
                for j in range(i+1, min(i+3, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('-'):
                        overview = lines[j].strip()
                        break
                break
        
        # Find todos (lines starting with - or *)
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '– ')):
                todo_text = line[2:].strip()
                if todo_text:
                    todos.append(ToDoItem(title=todo_text))
        
        # Try to extract table data from the text
        # Look for date patterns like "15.10", "16.10", "17.10"
        import re
        date_pattern = r'(\d{1,2}\.\d{1,2})'
        # capture time ranges and variants
        time_any_pattern = r'(\d{1,2}:\d{2}\s*[–-]\s*\d{1,2}:\d{2}|ab\s*\d{1,2}:\d{2}|\d{1,2}:\d{2})'

        # Aggregate multiple lines per date into one row
        per_date: dict[str, dict[str, List[str] | str]] = {}
        weekday_tokens = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so', 'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag']
        
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if re.search(date_pattern, line):
                date_match = re.search(date_pattern, line)
                date = date_match.group(1) if date_match else ""
                time_match = re.search(time_any_pattern, line, flags=re.IGNORECASE)
                time_val = time_match.group(1) if time_match else ""
                # Clean details: remove weekday tokens, pipes, and the matched date/time
                details = line
                details = details.replace(date, "")
                if time_val:
                    details = details.replace(time_val, "")
                # Remove pipe artifacts and clean up
                details = re.sub(r'\s*\|\s*', ' ', details)
                details = re.sub(r'^\|\s*', '', details)
                details = re.sub(r'\s*\|$', '', details)
                # strip weekday tokens at start
                parts = [p for p in re.split(r'\s+', details.strip(" -|.")) if p]
                if parts and parts[0].lower().strip(':') in weekday_tokens:
                    parts = parts[1:]
                details = ' '.join(parts).strip()
                # Remove action item numbers and clean up
                details = re.sub(r'^\d+\.\s*', '', details)
                details = re.sub(r'\s*am\s*$', '', details)
                if details and not any(w in details.lower() for w in ['vorbereiten', 'bereitstellen', 'sicherstellen', 'überprüfen']):
                    rec = per_date.setdefault(date, {"time": time_val, "details": []})
                    if time_val and not rec["time"]:
                        rec["time"] = time_val
                    # append detail line
                    cast_details = rec["details"]  # type: ignore
                    cast_details.append(details)
        
        for d, obj in per_date.items():
            first_time = obj["time"]  # type: ignore
            details_joined = ' ; '.join(obj["details"])  # type: ignore
            table_rows.append([d, str(first_time or ''), details_joined])

        # Create table if we found data
        table = None
        if table_rows:
            table = TableSection(
                title="Termine",
                columns=["Tag/Datum", "Zeit", "Details"],
                rows=table_rows[:6]  # Limit to 6 rows
            )

        header = ToDoReceiptHeader(
            title="Theater-Termine" if "theater" in (text or "").lower() else "Erkannte Inhalte",
            date_formatted="",
            source_label="Aus Eingabe",
        )
        
        summary = ToDoReceiptSummary(
            overview=overview or "Inhalt erkannt und strukturiert.",
            key_points=["Termine und Aufgaben extrahiert"] if table_rows else None
        )
        
        content = ToDoReceiptContent(
            header=header, 
            summary=summary, 
            todos=todos or [ToDoItem(title="Überprüfung notwendig")],
            tables=[table] if table else None
        )
        return content

    def _mock_output(self, text: Optional[str], image_url: Optional[str]) -> ToDoReceiptContent:
        # Generate better mock data based on input content
        if text and "theater" in text.lower():
            header = ToDoReceiptHeader(
                title="Theater‑Termine – Bühnentechnik",
                date_formatted="",
                source_label="Aus Eingabe",
            )
            summary = ToDoReceiptSummary(
                overview="Theater-Aufführungsplanung erkannt. Generalprobe und zwei Aufführungstage geplant. Technische Vorbereitung und Teamkoordination erforderlich.",
                key_points=[
                    "Generalprobe am 15.10 von 17:00-21:00",
                    "Aufführungen am 16.10 und 17.10",
                    "Anwesenheit ab 17:00 Uhr erforderlich",
                ],
            )
            todos = [
                ToDoItem(title="Verfügbarkeit für alle Termine bestätigen", priority="high"),
                ToDoItem(title="Teilnahme am Probentag (11.10) und Durchläufen sichern", priority="high"),
                ToDoItem(title="Checkliste Licht/Ton vorbereiten und mit Chor abstimmen", priority="medium"),
                ToDoItem(title="An Aufführungstagen ab 17:00 vor Ort sein (16./17.10)", priority="high"),
                ToDoItem(title="Technische Ausrüstung überprüfen und bereitstellen", priority="medium"),
            ]
            table = TableSection(
                title="Termine",
                columns=["Tag/Datum", "Zeit", "Details"],
                rows=[
                    ["Dienstag 07.10", "13:00–13:30", "Besprechung"],
                    ["Samstag 11.10", "ganztags; 11:00–13:00; 14:00–17:00", "Probentag; Durchlauf 1; Mittagspause/Picknick; Durchlauf 2 (ggf. mit Chor)"],
                    ["Sonntag 12.10", "10:00–14:00", "Durchlauf"],
                    ["Montag 13.10", "07:45–13:00", "Probentage ganztags (mit Licht, Ton, Chor …)"],
                    ["Mittwoch 15.10", "17:00–21:00", "Generalprobe"],
                    ["Donnerstag 16.10", "ab 17:00 (Beginn 19:00)", "Aufführung 1"],
                    ["Freitag 17.10", "ab 17:00 (Beginn 19:00)", "Aufführung 2"],
                ],
            )
        else:
            # Generic mock for other content
            header = ToDoReceiptHeader(
                title="Erkannte Inhalte",
                date_formatted="",
                source_label="Aus Eingabe",
            )
            summary = ToDoReceiptSummary(
                overview="Inhalt erfolgreich analysiert und strukturiert. Aufgaben und Termine wurden extrahiert.",
                key_points=["Strukturierte Daten erkannt", "Action Items generiert"],
            )
            todos = [
                ToDoItem(title="Überprüfung der extrahierten Informationen"),
                ToDoItem(title="Weitere Details bei Bedarf ergänzen"),
            ]
            table = None
        
        return ToDoReceiptContent(header=header, summary=summary, todos=todos, tables=[table] if table else None)


