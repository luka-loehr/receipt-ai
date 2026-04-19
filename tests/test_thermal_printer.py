import unittest
import sys
import types

from src.models import CompleteReceiptContent, PrintableContent

if "escpos" not in sys.modules:
    fake_escpos = types.ModuleType("escpos")
    fake_escpos.printer = types.SimpleNamespace()
    sys.modules["escpos"] = fake_escpos

if "escpos.exceptions" not in sys.modules:
    fake_exceptions = types.ModuleType("escpos.exceptions")
    fake_exceptions.Error = Exception
    sys.modules["escpos.exceptions"] = fake_exceptions

from src.thermal_printer import ThermalPrinter, build_demo_daily_brief


class ThermalPrinterTests(unittest.TestCase):
    def test_wrap_text_preserves_words_when_possible(self) -> None:
        printer = ThermalPrinter.__new__(ThermalPrinter)

        wrapped = printer._wrap_text("one two three four", max_chars=7)

        self.assertEqual(wrapped, "one two\nthree\nfour")

    def test_build_demo_daily_brief_returns_valid_models(self) -> None:
        receipt_content, printable_content = build_demo_daily_brief()

        self.assertIsInstance(receipt_content, CompleteReceiptContent)
        self.assertIsInstance(printable_content, PrintableContent)
        self.assertEqual(printable_content.receipt_content, receipt_content)
        self.assertEqual(len(printable_content.printable_tasks), 2)
        self.assertEqual(len(printable_content.printable_shopping), 1)


if __name__ == "__main__":
    unittest.main()
