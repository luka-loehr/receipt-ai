import unittest
from unittest.mock import patch

from src.config import AppConfig
from src.services.task_service import TaskService
from src.services.weather_service import WeatherService


class ServiceFallbackTests(unittest.TestCase):
    @patch("src.services.weather_service.requests.get")
    def test_weather_service_returns_none_without_key_when_mock_disabled(self, _mock_get) -> None:
        service = WeatherService(AppConfig(allow_mock_data=False))

        self.assertIsNone(service.get_current_weather())

    @patch("src.services.task_service.os.path.exists", return_value=False)
    def test_task_service_returns_empty_without_token_when_mock_disabled(self, _mock_exists) -> None:
        service = TaskService(AppConfig(allow_mock_data=False))

        self.assertEqual(service.get_tasks(), [])
        self.assertEqual(service.get_shopping_list(), [])

    @patch("src.services.task_service.os.path.exists", return_value=False)
    def test_task_service_can_return_mock_data_in_demo_mode(self, _mock_exists) -> None:
        service = TaskService(AppConfig(allow_mock_data=True))

        self.assertGreater(len(service.get_tasks()), 0)
        self.assertGreater(len(service.get_shopping_list()), 0)


if __name__ == "__main__":
    unittest.main()
