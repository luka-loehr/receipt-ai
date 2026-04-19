import unittest

from src.path_utils import path_to_file_url


class CaptureGenerateTests(unittest.TestCase):
    def test_path_to_file_url_creates_file_scheme(self) -> None:
        url = path_to_file_url("sample folder/example image.png")

        self.assertTrue(url.startswith("file:"))
        self.assertIn("sample%20folder", url)
        self.assertIn("example%20image.png", url)


if __name__ == "__main__":
    unittest.main()
