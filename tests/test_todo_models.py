import unittest

from src.todo_models import ToDoReceiptHeader


class ToDoModelsTests(unittest.TestCase):
    def test_header_title_is_capped_for_receipt_layout(self) -> None:
        header = ToDoReceiptHeader(
            title="X" * 80,
            date_formatted="Sunday, 2026-04-19",
        )

        self.assertLessEqual(len(header.title), 48)


if __name__ == "__main__":
    unittest.main()
