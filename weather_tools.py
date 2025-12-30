"""Weather API integration using OpenWeatherMap."""

import os
import requests
from typing import Optional


class WeatherAPI:
    """Client for OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required")

    def _get_coordinates(self, location: str) -> tuple[float, float, str]:
        """Convert location name to coordinates."""
        response = requests.get(
            f"{self.GEO_URL}/direct",
            params={"q": location, "limit": 1, "appid": self.api_key},
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"Location '{location}' not found")

        return data[0]["lat"], data[0]["lon"], data[0].get("name", location)

    def get_current_weather(self, location: str, units: str = "metric") -> dict:
        """
        Get current weather for a location.

        Args:
            location: City name or location string (e.g., "London" or "London, UK")
            units: Temperature units - 'metric' (Celsius), 'imperial' (Fahrenheit)

        Returns:
            Dictionary with current weather data
        """
        lat, lon, name = self._get_coordinates(location)

        response = requests.get(
            f"{self.BASE_URL}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units,
            },
        )
        response.raise_for_status()
        data = response.json()

        temp_unit = "°C" if units == "metric" else "°F"
        speed_unit = "m/s" if units == "metric" else "mph"

        return {
            "location": name,
            "temperature": f"{data['main']['temp']}{temp_unit}",
            "feels_like": f"{data['main']['feels_like']}{temp_unit}",
            "humidity": f"{data['main']['humidity']}%",
            "description": data["weather"][0]["description"].capitalize(),
            "wind_speed": f"{data['wind']['speed']} {speed_unit}",
            "pressure": f"{data['main']['pressure']} hPa",
        }

    def get_forecast(
        self, location: str, days: int = 5, units: str = "metric"
    ) -> dict:
        """
        Get weather forecast for a location.

        Args:
            location: City name or location string
            days: Number of days to forecast (1-5)
            units: Temperature units - 'metric' (Celsius), 'imperial' (Fahrenheit)

        Returns:
            Dictionary with forecast data
        """
        lat, lon, name = self._get_coordinates(location)

        response = requests.get(
            f"{self.BASE_URL}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units,
            },
        )
        response.raise_for_status()
        data = response.json()

        temp_unit = "°C" if units == "metric" else "°F"

        # Group forecasts by day
        daily_forecasts = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "date": date,
                    "temps": [],
                    "descriptions": [],
                    "humidity": [],
                }
            daily_forecasts[date]["temps"].append(item["main"]["temp"])
            daily_forecasts[date]["descriptions"].append(
                item["weather"][0]["description"]
            )
            daily_forecasts[date]["humidity"].append(item["main"]["humidity"])

        # Summarize each day
        forecast_list = []
        for date, day_data in list(daily_forecasts.items())[:days]:
            temps = day_data["temps"]
            forecast_list.append(
                {
                    "date": date,
                    "high": f"{max(temps):.1f}{temp_unit}",
                    "low": f"{min(temps):.1f}{temp_unit}",
                    "avg_humidity": f"{sum(day_data['humidity']) / len(day_data['humidity']):.0f}%",
                    "conditions": most_common(day_data["descriptions"]).capitalize(),
                }
            )

        return {"location": name, "forecast": forecast_list}


def most_common(lst: list) -> str:
    """Return the most common element in a list."""
    return max(set(lst), key=lst.count)


# Tool definitions for Claude
WEATHER_TOOLS = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather conditions for a specific location. Returns temperature, humidity, wind speed, and weather description.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name or location (e.g., 'London', 'New York, US', 'Tokyo, Japan')",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "Temperature units: 'metric' for Celsius, 'imperial' for Fahrenheit. Defaults to metric.",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_forecast",
        "description": "Get the weather forecast for the next few days for a specific location. Returns daily high/low temperatures and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name or location (e.g., 'London', 'New York, US', 'Tokyo, Japan')",
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Number of days to forecast (1-5). Defaults to 5.",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "Temperature units: 'metric' for Celsius, 'imperial' for Fahrenheit. Defaults to metric.",
                },
            },
            "required": ["location"],
        },
    },
]
