import base64
import sys
import tempfile
import types
import unittest
from pathlib import Path

from src.todo_models import TableSection, ToDoItem

if "openai" not in sys.modules:
    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = object
    sys.modules["openai"] = fake_openai

from src.capture_ai import CaptureAI, CaptureAnalysisResult


class CaptureAITests(unittest.TestCase):
    def test_prepare_user_parts_converts_local_file_url_to_data_url(self) -> None:
        ai = CaptureAI.__new__(CaptureAI)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
            image_file.write(b"png-bytes")
            image_path = Path(image_file.name)

        try:
            parts = ai._prepare_user_parts(None, image_path.as_uri())
        finally:
            image_path.unlink(missing_ok=True)

        self.assertEqual(parts[0]["type"], "image_url")
        url = parts[0]["image_url"]["url"]
        self.assertTrue(url.startswith("data:image/png;base64,"))
        self.assertEqual(url.split(",", 1)[1], base64.b64encode(b"png-bytes").decode("ascii"))

    def test_build_content_uses_structured_result_without_regex_parsing(self) -> None:
        ai = CaptureAI.__new__(CaptureAI)
        result = CaptureAnalysisResult(
            title="Probeplan",
            overview="Zwei Termine erkannt.",
            key_points=["Generalprobe", "Auffuehrung"],
            todos=[ToDoItem(title="Technik pruefen")],
            tables=[
                TableSection(
                    title="Termine",
                    columns=["Tag/Datum", "Zeit", "Details"],
                    rows=[["15.10", "17:00-21:00", "Generalprobe"]],
                )
            ],
        )

        content = ai._build_content("theater plan", result)

        self.assertEqual(content.header.title, "Probeplan")
        self.assertEqual(content.summary.overview, "Zwei Termine erkannt.")
        self.assertEqual(content.todos[0].title, "Technik pruefen")
        self.assertEqual(content.tables[0].rows[0][2], "Generalprobe")


if __name__ == "__main__":
    unittest.main()
