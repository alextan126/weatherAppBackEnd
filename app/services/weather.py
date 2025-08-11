import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Get current weather for given coordinates
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            print(f"Error getting current weather: {e}")
            return None
    
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for given coordinates
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",
                        "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            print(f"Error getting forecast: {e}")
            return None
    
    async def get_historical_weather(self, lat: float, lon: float, dt: int) -> Optional[Dict[str, Any]]:
        """
        Get historical weather for given coordinates and timestamp
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/onecall/timemachine",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",
                        "dt": dt
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            print(f"Error getting historical weather: {e}")
            return None
    
    def parse_weather_data(self, weather_data: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """
        Parse weather API response into standardized format
        """
        if request_type == "current":
            return self._parse_current_weather(weather_data)
        elif request_type == "forecast":
            return self._parse_forecast_weather(weather_data)
        elif request_type == "historical":
            return self._parse_historical_weather(weather_data)
        else:
            return weather_data
    
    def _parse_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse current weather data"""
        try:
            return {
                "temperature": data.get("main", {}).get("temp"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "wind_direction": data.get("wind", {}).get("deg"),
                "description": data.get("weather", [{}])[0].get("description"),
                "icon": data.get("weather", [{}])[0].get("icon"),
                "raw_data": data
            }
        except Exception as e:
            print(f"Error parsing current weather: {e}")
            return {"raw_data": data}
    
    def _parse_forecast_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse forecast weather data"""
        try:
            # Return first forecast entry as representative
            if data.get("list") and len(data["list"]) > 0:
                first_forecast = data["list"][0]
                return {
                    "temperature": first_forecast.get("main", {}).get("temp"),
                    "humidity": first_forecast.get("main", {}).get("humidity"),
                    "pressure": first_forecast.get("main", {}).get("pressure"),
                    "wind_speed": first_forecast.get("wind", {}).get("speed"),
                    "wind_direction": first_forecast.get("wind", {}).get("deg"),
                    "description": first_forecast.get("weather", [{}])[0].get("description"),
                    "icon": first_forecast.get("weather", [{}])[0].get("icon"),
                    "forecast_date": first_forecast.get("dt_txt"),
                    "raw_data": data
                }
            return {"raw_data": data}
        except Exception as e:
            print(f"Error parsing forecast weather: {e}")
            return {"raw_data": data}
    
    def _parse_historical_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse historical weather data"""
        try:
            if data.get("data") and len(data["data"]) > 0:
                historical = data["data"][0]
                return {
                    "temperature": historical.get("temp"),
                    "humidity": historical.get("humidity"),
                    "pressure": historical.get("pressure"),
                    "wind_speed": historical.get("wind_speed"),
                    "wind_direction": historical.get("wind_deg"),
                    "description": historical.get("weather", [{}])[0].get("description"),
                    "icon": historical.get("weather", [{}])[0].get("icon"),
                    "raw_data": data
                }
            return {"raw_data": data}
        except Exception as e:
            print(f"Error parsing historical weather: {e}")
            return {"raw_data": data}


weather_service = WeatherService() 