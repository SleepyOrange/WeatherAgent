#!/usr/bin/env python3
"""Weather Agent MCP Server - Exposes weather tools via Model Context Protocol."""

import json
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from weather_tools import WeatherAPI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("weather-agent")

# Initialize weather API client
weather_api = WeatherAPI()


@mcp.tool()
def get_current_weather(location: str, units: str = "metric") -> str:
    """
    Get current weather conditions for a location.

    Args:
        location: City name or location (e.g., 'London', 'New York, US', 'Tokyo, Japan')
        units: Temperature units - 'metric' for Celsius, 'imperial' for Fahrenheit

    Returns:
        Current weather data including temperature, humidity, wind speed, and conditions
    """
    try:
        result = weather_api.get_current_weather(location, units)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_forecast(location: str, days: int = 5, units: str = "metric") -> str:
    """
    Get weather forecast for the next few days.

    Args:
        location: City name or location (e.g., 'London', 'New York, US', 'Tokyo, Japan')
        days: Number of days to forecast (1-5)
        units: Temperature units - 'metric' for Celsius, 'imperial' for Fahrenheit

    Returns:
        Weather forecast with daily high/low temperatures and conditions
    """
    try:
        days = max(1, min(5, days))  # Clamp to 1-5
        result = weather_api.get_forecast(location, days, units)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()

# this is the end of the file
