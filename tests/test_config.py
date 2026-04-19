import os
import unittest
from unittest.mock import patch

from src.config import AppConfig


class AppConfigTests(unittest.TestCase):
    def test_from_environment_reads_expected_values(self) -> None:
        env = {
            "RECEIPT_LANGUAGE": "english",
            "USER_NAME": "Ada",
            "USER_TIMEZONE": "UTC",
            "AI_MODEL": "gpt-4o-mini",
            "MAX_OUTPUT_TOKENS": "900",
            "WEATHER_LOCATION": "Berlin,DE",
            "MAX_EMAILS_TO_PROCESS": "7",
            "MAX_TASKS_TO_PROCESS": "11",
            "GENERAL_TASKS_LIST_NAME": "General",
            "SHOPPING_LIST_NAME": "Groceries",
            "THERMAL_PRINTER_TYPE": "file",
            "PAPER_WIDTH_MM": "80",
            "OUTPUT_PNG_FILE": "out/test.png",
            "OUTPUT_TXT_FILE": "out/test.txt",
            "OUTPUT_ESCPOS_FILE": "out/test.escpos",
        }

        with patch.dict(os.environ, env, clear=True):
            config = AppConfig.from_environment()

        self.assertEqual(config.language, "english")
        self.assertEqual(config.user_name, "Ada")
        self.assertEqual(config.timezone, "UTC")
        self.assertEqual(config.max_tokens, 900)
        self.assertEqual(config.max_emails_to_process, 7)
        self.assertEqual(config.max_tasks_to_process, 11)
        self.assertEqual(config.shopping_list_name, "Groceries")
        self.assertEqual(config.paper_width_mm, 80)
        self.assertEqual(config.output_png_file, "out/test.png")

    def test_get_language_code_title_cases_value(self) -> None:
        config = AppConfig(language="german")

        self.assertEqual(config.get_language_code(), "German")


if __name__ == "__main__":
    unittest.main()
