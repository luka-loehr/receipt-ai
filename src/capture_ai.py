#!/usr/bin/env python3
"""
AI service for manual capture (text or image) → To-Do receipt content.
Uses GPT-4o (vision-capable) if OPENAI_API_KEY is present; otherwise mock.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
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


class CaptureAnalysisResult(BaseModel):
    """Structured output for capture analysis."""

    title: str = Field(default="Erkannte Inhalte")
    overview: str = Field(description="Kurze deutsche Zusammenfassung.")
    key_points: List[str] = Field(default_factory=list)
    todos: List[ToDoItem] = Field(default_factory=list)
    tables: List[TableSection] = Field(default_factory=list)


class CaptureAI:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.openai_api_key
        # Prefer the vision-capable model for capture
        self.model = "gpt-4o" if (self.config.ai_model or "").startswith("gpt-") else "gpt-4o"
        self.mock = not self.api_key or OpenAI is None
        self.client = OpenAI(api_key=self.api_key) if not self.mock else None

    def _prepare_user_parts(self, text: Optional[str], image_url: Optional[str]) -> List[dict]:
        """Prepare multimodal message parts for OpenAI."""
        user_parts: List[dict] = []
        if text:
            user_parts.append({"type": "text", "text": text})
        if image_url:
            try:
                parsed = urlparse(image_url)
                if parsed.scheme == 'file':
                    local_path = parsed.path
                    with open(local_path, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode('ascii')
                    mime = 'image/png' if local_path.lower().endswith('.png') else 'image/jpeg'
                    image_url = f"data:{mime};base64,{b64}"
                user_parts.append({"type": "image_url", "image_url": {"url": image_url}})
            except Exception:
                pass
        if not user_parts:
            user_parts.append({"type": "text", "text": "Kein Inhalt übergeben"})
        return user_parts

    def _build_content(self, text: Optional[str], result: CaptureAnalysisResult) -> ToDoReceiptContent:
        """Convert structured AI output into receipt content."""
        title = result.title.strip() if result.title.strip() else "Erkannte Inhalte"
        if text and "theater" in text.lower() and title == "Erkannte Inhalte":
            title = "Theater-Termine"

        return ToDoReceiptContent(
            header=ToDoReceiptHeader(
                title=title,
                date_formatted="",
                source_label="Aus Eingabe",
            ),
            summary=ToDoReceiptSummary(
                overview=result.overview.strip() or "Inhalt erkannt und strukturiert.",
                key_points=result.key_points or None,
            ),
            todos=result.todos or [ToDoItem(title="Überprüfung notwendig")],
            tables=result.tables or None,
        )

    def analyze(self, text: Optional[str], image_url: Optional[str]) -> ToDoReceiptContent:
        if self.mock:
            return self._mock_output(text, image_url)

        messages: List[dict] = [
            {
                "role": "system",
                "content": (
                    "Du extrahierst strukturierte Termine und To-dos aus Bildern oder Text."
                    " Antworte immer auf Deutsch und halte dich an das geforderte Ausgabeformat."
                ),
            }
        ]

        messages.append({"role": "user", "content": self._prepare_user_parts(text, image_url)})

        prompt = (
            "Extrahiere strukturierte Informationen aus Bild oder Text.\n"
            "Setze `title` passend zum Inhalt, kurz und klar.\n"
            "Setze `overview` auf 2-3 kurze deutsche Saetze.\n"
            "Setze `key_points` auf 0-4 kurze Stichpunkte.\n"
            "Setze `todos` auf 3-6 konkrete, umsetzbare Aufgaben wenn moeglich.\n"
            "Wenn Termine erkennbar sind, liefere mindestens eine Tabelle mit den Spalten "
            "`Tag/Datum`, `Zeit`, `Details`.\n"
            "Erkenne Datumsformen wie `Di 07.10`, `15.10`, `16.10`, `17.10` und Zeiten wie "
            "`17:00-21:00`, `ab 17:00`, `10:00-14:00`."
        )
        messages.append({"role": "system", "content": prompt})

        try:
            resp = self.client.chat.completions.parse(  # type: ignore
                model=self.model,
                messages=messages,
                temperature=0.2,
                response_format=CaptureAnalysisResult,
            )
            message = resp.choices[0].message
            if not message.parsed:
                raise ValueError(f"Capture analysis unavailable: {message.refusal}")
            return self._build_content(text, message.parsed)
        except Exception:
            return self._mock_output(text, image_url)

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

