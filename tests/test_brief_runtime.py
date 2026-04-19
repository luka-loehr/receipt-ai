import tempfile
import unittest
from pathlib import Path

from src.brief_runtime import build_text_brief_content, save_text_brief
from src.models import (
    CompleteReceiptContent,
    PrintableContent,
    PrintableShoppingItem,
    PrintableTask,
    ReceiptFooter,
    ReceiptHeader,
    ReceiptSummary,
    ShoppingSection,
    TaskSection,
)


def make_receipt() -> tuple[CompleteReceiptContent, PrintableContent]:
    receipt = CompleteReceiptContent(
        header=ReceiptHeader(
            greeting="Hallo Luka",
            title="Tagesbrief",
            date_formatted="Sonntag, 19. April 2026",
        ),
        summary=ReceiptSummary(brief="Heute stehen zwei Dinge an."),
        task_section=TaskSection(section_title="Aufgaben"),
        shopping_section=ShoppingSection(section_title="Einkauf"),
        footer=ReceiptFooter(footer_text="Generiert"),
    )
    printable = PrintableContent(
        receipt_content=receipt,
        printable_tasks=[
            PrintableTask(
                display_text="E-Mails beantworten",
                is_truncated=False,
                original_title="E-Mails beantworten",
            )
        ],
        printable_shopping=[
            PrintableShoppingItem(
                display_text="Hafermilch",
                is_truncated=False,
                original_title="Hafermilch",
            )
        ],
    )
    return receipt, printable


class BriefRuntimeTests(unittest.TestCase):
    def test_build_text_brief_content_includes_sections(self) -> None:
        receipt, printable = make_receipt()

        text = build_text_brief_content(receipt, printable)

        self.assertIn("Hallo Luka", text)
        self.assertIn("Aufgaben", text)
        self.assertIn("E-Mails beantworten", text)
        self.assertIn("Einkauf", text)
        self.assertIn("Hafermilch", text)

    def test_save_text_brief_writes_output_file(self) -> None:
        receipt, printable = make_receipt()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "out" / "brief.txt"
            saved_path = save_text_brief(receipt, printable, str(output_path))

            self.assertEqual(saved_path, str(output_path))
            self.assertTrue(output_path.exists())
            self.assertIn("Tagesbrief", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
