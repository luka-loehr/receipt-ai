import unittest
import sys
import types

from src.config import AppConfig

if "openai" not in sys.modules:
    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = object
    sys.modules["openai"] = fake_openai

from src.data_manager import ModularDataManager


class DataManagerTests(unittest.TestCase):
    def test_set_language_updates_config_without_enum_dependency(self) -> None:
        config = AppConfig(language="german", allow_mock_data=False)
        manager = ModularDataManager(config)

        manager.set_language("english")

        self.assertEqual(config.language, "english")


if __name__ == "__main__":
    unittest.main()
