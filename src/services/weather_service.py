#!/usr/bin/env python3
"""
Weather Service Module
Handles weather data fetching from OpenWeatherMap One Call API 3.0
"""

import os
import requests
from typing import Tuple
from ..models import WeatherData
from ..config import AppConfig


class WeatherService:
    """Handles weather data fetching from OpenWeatherMap One Call API 3.0"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = config.openweather_api_key
        self.location = config.weather_location
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        
        if not self.api_key:
            print("⚠️  Warning: No OpenWeatherMap API key found. Weather data will be mocked.")
    
    def _get_weather_icon(self, weather_code: str, is_day: bool = True) -> str:
        """Map OpenWeather weather codes to ASCII-compatible icons"""
        # OpenWeather weather codes mapping to ASCII characters for thermal printer compatibility
        icon_map = {
            # Clear sky
            "01d": "[SUN]",  # clear sky day
            "01n": "[MOON]",  # clear sky night
            
            # Few clouds
            "02d": "[SUN_CLOUD]",  # few clouds day
            "02n": "[CLOUD]",  # few clouds night
            
            # Scattered clouds
            "03d": "[CLOUD]",  # scattered clouds
            "03n": "[CLOUD]",
            
            # Broken clouds
            "04d": "[CLOUD]",  # broken clouds
            "04n": "[CLOUD]",
            
            # Shower rain
            "09d": "[RAIN]",  # shower rain
            "09n": "[RAIN]",
            
            # Rain
            "10d": "[RAIN]",  # rain day
            "10n": "[RAIN]",  # rain night
            
            # Thunderstorm
            "11d": "[STORM]",  # thunderstorm
            "11n": "[STORM]",
            
            # Snow
            "13d": "[SNOW]",  # snow
            "13n": "[SNOW]",
            
            # Mist
            "50d": "[FOG]",  # mist
            "50n": "[FOG]",
        }
        
        return icon_map.get(weather_code, "[WEATHER]")  # Default icon
    
    def _get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates for the location using Geocoding API"""
        geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': self.location,
            'appid': self.api_key,
            'limit': 1
        }
        
        response = requests.get(geocoding_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise Exception(f"Location '{self.location}' not found")
        
        return data[0]['lat'], data[0]['lon']
    
    def get_current_weather(self) -> WeatherData:
        """Get current weather data using One Call API 3.0"""
        if not self.api_key:
            return self._get_mock_weather()
        
        try:
            # Get coordinates for the location
            lat, lon = self._get_coordinates()
            
            # Use One Call API 3.0
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'exclude': 'minutely,alerts'  # Exclude unnecessary data to save API calls
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract current weather
            current = data['current']
            daily = data['daily'][0]  # Today's forecast

            # Get weather icon
            weather_icon = current['weather'][0]['icon']
            icon_emoji = self._get_weather_icon(weather_icon)

            # Create weather history summary (ASCII only, no degree symbol)
            weather_history = f"Min: {round(daily['temp']['min'])} C, Max: {round(daily['temp']['max'])} C"

            # Get tomorrow's forecast if available
            tomorrow_forecast = ""
            if len(data['daily']) > 1:
                tomorrow = data['daily'][1]
                tomorrow_temp_min = round(tomorrow['temp']['min'])
                tomorrow_temp_max = round(tomorrow['temp']['max'])
                tomorrow_condition = tomorrow['weather'][0]['description'].title()
                tomorrow_forecast = f"{tomorrow_condition}, {tomorrow_temp_min}-{tomorrow_temp_max} C"

            return WeatherData(
                temperature=f"{round(current['temp'])} C",
                condition=current['weather'][0]['description'].title(),
                high=f"{round(daily['temp']['max'])} C",
                low=f"{round(daily['temp']['min'])} C",
                humidity=f"{current['humidity']}%",
                wind_speed=f"{round(current['wind_speed'] * 3.6, 1)} km/h",  # Convert m/s to km/h
                feels_like=f"{round(current['feels_like'])} C",
                icon=icon_emoji,
                history=weather_history,
                tomorrow_forecast=tomorrow_forecast
            )
            
        except Exception as e:
            print(f"⚠️  Weather API error: {e}")
            return self._get_mock_weather()
    
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
            icon="[CLOUD]",
            history="Min: 14 C, Max: 22 C",
            tomorrow_forecast="Sunny, 16-24 C"
        )


def create_weather_service(config: AppConfig) -> WeatherService:
    """Factory function to create weather service"""
    return WeatherService(config)
