#!/usr/bin/env python3
"""
Weather Service Module
Handles weather data fetching from Open-Meteo APIs
"""

import requests
from typing import Optional, Tuple
from ..models import WeatherData
from ..config import AppConfig

WEATHER_CODE_MAP = {
    0: ("Clear Sky", "[SUN]", "[MOON]"),
    1: ("Mainly Clear", "[SUN]", "[MOON]"),
    2: ("Partly Cloudy", "[SUN_CLOUD]", "[CLOUD]"),
    3: ("Overcast", "[CLOUD]", "[CLOUD]"),
    45: ("Fog", "[FOG]", "[FOG]"),
    48: ("Rime Fog", "[FOG]", "[FOG]"),
    51: ("Light Drizzle", "[RAIN]", "[RAIN]"),
    53: ("Drizzle", "[RAIN]", "[RAIN]"),
    55: ("Dense Drizzle", "[RAIN]", "[RAIN]"),
    56: ("Freezing Drizzle", "[SNOW]", "[SNOW]"),
    57: ("Dense Freezing Drizzle", "[SNOW]", "[SNOW]"),
    61: ("Light Rain", "[RAIN]", "[RAIN]"),
    63: ("Rain", "[RAIN]", "[RAIN]"),
    65: ("Heavy Rain", "[RAIN]", "[RAIN]"),
    66: ("Light Freezing Rain", "[SNOW]", "[SNOW]"),
    67: ("Heavy Freezing Rain", "[SNOW]", "[SNOW]"),
    71: ("Light Snow", "[SNOW]", "[SNOW]"),
    73: ("Snow", "[SNOW]", "[SNOW]"),
    75: ("Heavy Snow", "[SNOW]", "[SNOW]"),
    77: ("Snow Grains", "[SNOW]", "[SNOW]"),
    80: ("Rain Showers", "[RAIN]", "[RAIN]"),
    81: ("Rain Showers", "[RAIN]", "[RAIN]"),
    82: ("Heavy Rain Showers", "[RAIN]", "[RAIN]"),
    85: ("Snow Showers", "[SNOW]", "[SNOW]"),
    86: ("Heavy Snow Showers", "[SNOW]", "[SNOW]"),
    95: ("Thunderstorm", "[STORM]", "[STORM]"),
    96: ("Thunderstorm With Hail", "[STORM]", "[STORM]"),
    99: ("Severe Thunderstorm", "[STORM]", "[STORM]"),
}


class WeatherService:
    """Handles weather data fetching from Open-Meteo APIs."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.location = config.weather_location
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
    
    def _get_weather_details(self, weather_code: int, is_day: bool) -> Tuple[str, str]:
        """Map WMO weather codes to display labels and ASCII-friendly icons."""
        description, day_icon, night_icon = WEATHER_CODE_MAP.get(
            weather_code,
            ("Weather Unavailable", "[WEATHER]", "[WEATHER]"),
        )
        return description, day_icon if is_day else night_icon
    
    def _get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates for the location using Open-Meteo geocoding."""
        params = {
            'name': self.location,
            'count': 1,
            'language': 'de' if self.config.language == 'german' else 'en',
            'format': 'json',
        }
        
        response = requests.get(self.geocoding_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        if not results:
            raise Exception(f"Location '{self.location}' not found")
        
        return results[0]['latitude'], results[0]['longitude']
    
    def get_current_weather(self) -> Optional[WeatherData]:
        """Get current weather data using Open-Meteo forecast APIs."""
        try:
            lat, lon = self._get_coordinates()
            params = {
                'lat': lat,
                'lon': lon,
                'current': 'temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,is_day',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
                'forecast_days': 2,
                'temperature_unit': 'celsius',
                'wind_speed_unit': 'kmh',
                'timezone': self.config.timezone,
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current']
            daily = data['daily']
            today_high = round(daily['temperature_2m_max'][0])
            today_low = round(daily['temperature_2m_min'][0])
            condition, icon = self._get_weather_details(
                int(current['weather_code']),
                bool(current.get('is_day', 1)),
            )
            weather_history = f"Min: {today_low} C, Max: {today_high} C"
            tomorrow_forecast = ""
            if len(daily['weather_code']) > 1:
                tomorrow_condition, _ = self._get_weather_details(int(daily['weather_code'][1]), True)
                tomorrow_temp_min = round(daily['temperature_2m_min'][1])
                tomorrow_temp_max = round(daily['temperature_2m_max'][1])
                tomorrow_forecast = f"{tomorrow_condition}, {tomorrow_temp_min}-{tomorrow_temp_max} C"

            return WeatherData(
                temperature=f"{round(current['temperature_2m'])} C",
                condition=condition,
                high=f"{today_high} C",
                low=f"{today_low} C",
                humidity=f"{round(current['relative_humidity_2m'])}%",
                wind_speed=f"{round(current['wind_speed_10m'], 1)} km/h",
                feels_like=f"{round(current['apparent_temperature'])} C",
                icon=icon,
                history=weather_history,
                tomorrow_forecast=tomorrow_forecast
            )
            
        except Exception as e:
            print(f"⚠️  Weather API error: {e}")
            return self._get_mock_weather() if self.config.allow_mock_data else None
    
    def _get_mock_weather(self) -> WeatherData:
        """Return mock weather data when API is unavailable"""
        return WeatherData(
            temperature="18 C",
            condition="Partly Cloudy",
            high="22 C",
            low="14 C",
            humidity="65%",
            wind_speed="12.0 km/h",
            feels_like="19 C",
            icon="[SUN_CLOUD]",
            history="Min: 14 C, Max: 22 C",
            tomorrow_forecast="Mainly Clear, 16-24 C"
        )


def create_weather_service(config: AppConfig) -> WeatherService:
    """Factory function to create weather service"""
    return WeatherService(config)
