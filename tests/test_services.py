import unittest
from unittest.mock import Mock, patch

from src.config import AppConfig
from src.services.task_service import TaskService
from src.services.weather_service import WeatherService


class ServiceFallbackTests(unittest.TestCase):
    @patch("src.services.weather_service.requests.get")
    def test_weather_service_returns_none_when_open_meteo_fails(self, mock_get) -> None:
        service = WeatherService(AppConfig(allow_mock_data=False))
        mock_get.side_effect = RuntimeError("network down")

        self.assertIsNone(service.get_current_weather())

    @patch("src.services.weather_service.requests.get")
    def test_weather_service_maps_open_meteo_response(self, mock_get) -> None:
        geocode_response = Mock()
        geocode_response.raise_for_status.return_value = None
        geocode_response.json.return_value = {
            "results": [{"latitude": 49.0, "longitude": 8.4}],
        }

        forecast_response = Mock()
        forecast_response.raise_for_status.return_value = None
        forecast_response.json.return_value = {
            "current": {
                "temperature_2m": 18.4,
                "apparent_temperature": 19.1,
                "relative_humidity_2m": 65,
                "wind_speed_10m": 12.3,
                "weather_code": 2,
                "is_day": 1,
            },
            "daily": {
                "weather_code": [2, 61],
                "temperature_2m_max": [22.0, 19.0],
                "temperature_2m_min": [14.0, 11.0],
            },
        }
        mock_get.side_effect = [geocode_response, forecast_response]

        service = WeatherService(AppConfig(allow_mock_data=False))
        weather = service.get_current_weather()

        self.assertIsNotNone(weather)
        self.assertEqual(weather.temperature, "18 C")
        self.assertEqual(weather.condition, "Partly Cloudy")
        self.assertEqual(weather.icon, "[SUN_CLOUD]")
        self.assertEqual(weather.tomorrow_forecast, "Light Rain, 11-19 C")

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
