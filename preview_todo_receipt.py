#!/usr/bin/env python3
"""
Preview the standalone To-Do / Capture receipt layout.
Generates a PNG at outputs/png/todo_capture.png.
"""

from datetime import datetime

from src.todo_models import (
    ToDoReceiptHeader,
    ToDoReceiptSummary,
    ToDoItem,
    ToDoReceiptContent,
    TableSection,
)
from src.todo_receipt import save_todo_receipt


def main():
    now = datetime.now().strftime("%A, %d. %B %Y • %H:%M")
    header = ToDoReceiptHeader(
        title="Theater‑Termine – Bühnentechnik",
        date_formatted=now,
        source_label="Aus Bild‑Upload",
    )

    summary = ToDoReceiptSummary(
        overview=(
            "Anfrage zur Unterstützung der Bühnentechnik für die Aufführung ‚Krabat‘ im Oktober. "
            "An allen aufgeführten Tagen wird Anwesenheit erwartet; vorherige Absprache zu Zuständigkeiten (Licht/Ton)."
        ),
        key_points=[
            "Ganztägiger Probentag und zwei Durchläufe (11.–12.10)",
            "Generalprobe am 15.10 von 17:00–21:00",
            "Aufführungen am 16.10 und 17.10, Anwesenheit ab 17:00 (Beginn 19:00)",
        ],
    )

    todos = [
        ToDoItem(title="Verfügbarkeit für alle Termine bestätigen", priority="high"),
        ToDoItem(title="Teilnahme am Probentag (11.10) und Durchläufen sichern", priority="high"),
        ToDoItem(title="Checkliste Licht/Ton vorbereiten und mit Chor abstimmen", priority="medium"),
        ToDoItem(title="An Aufführungstagen ab 17:00 vor Ort sein (16./17.10)", priority="high"),
    ]

    content = ToDoReceiptContent(
        header=header,
        summary=summary,
        todos=todos,
        tables=[
            TableSection(
                title="Übersicht",
                columns=["Tag/Datum", "Zeit", "Details"],
                rows=[
                    ["Dienstag 07.10", "13:00–13:30", "Besprechung"],
                    [
                        "Samstag 11.10",
                        "ganztags; 11:00–13:00; 14:00–17:00",
                        "Probentag; Durchlauf 1; Mittagspause/Picknick; Durchlauf 2 (ggf. mit Chor)",
                    ],
                    ["Sonntag 12.10", "10:00–14:00", "Durchlauf"],
                    ["Montag 13.10", "07:45–13:00", "Probentage ganztags (mit Licht, Ton, Chor …)"],
                    ["Mittwoch 15.10", "17:00–21:00", "Generalprobe"],
                    ["Donnerstag 16.10", "ab 17:00 (Beginn 19:00)", "Aufführung 1"],
                    ["Freitag 17.10", "ab 17:00 (Beginn 19:00)", "Aufführung 2"],
                ],
            )
        ],
    )

    out_path = save_todo_receipt(content)
    print(f"Generated preview: {out_path}")


if __name__ == "__main__":
    main()


