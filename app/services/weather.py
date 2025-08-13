import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OpenWeatherService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
    
    async def search_location(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for a location using OpenWeather Geocoding API"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.openweathermap.org/geo/1.0/direct",
                    params={
                        "q": query,
                        "limit": 5,
                        "appid": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data:
                    # Return the first (most relevant) result
                    location = data[0]
                    return {
                        "name": location["name"],
                        "country": location["country"],
                        "admin1": location.get("state"),
                        "latitude": location["lat"],
                        "longitude": location["lon"]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error searching location: {e}")
            return None
    
    async def get_historical_weather(
        self, 
        lat: float, 
        lon: float, 
        start_ts: datetime, 
        end_ts: datetime
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical weather data from OpenWeather API"""
        if not self.api_key:
            return None
            
        try:
            # OpenWeather historical data requires Unix timestamps
            start_unix = int(start_ts.timestamp())
            end_unix = int(end_ts.timestamp())
            
            # Get data for each day in range (OpenWeather provides daily data)
            observations = []
            current_ts = start_unix
            
            while current_ts <= end_unix:
                current_date = datetime.fromtimestamp(current_ts, tz=timezone.utc)
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/onecall/timemachine",
                        params={
                            "lat": lat,
                            "lon": lon,
                            "dt": current_ts,
                            "appid": self.api_key,
                            "units": "metric"  # Use Celsius
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract hourly data for this day
                    if "hourly" in data:
                        for hour_data in data["hourly"]:
                            hour_ts = datetime.fromtimestamp(hour_data["dt"], tz=timezone.utc)
                            
                            # Only include data within our requested range
                            if start_ts <= hour_ts <= end_ts:
                                observations.append({
                                    "ts": hour_ts,
                                    "temp_c": hour_data["temp"],
                                    "source": "openweather_api"
                                })
                
                # Move to next day (86400 seconds = 24 hours)
                current_ts += 86400
                
            return observations
            
        except Exception as e:
            logger.error(f"Error fetching historical weather: {e}")
            return None
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get current weather data"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temp_c": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"]
                }
                
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None

# Global instance
weather_service = OpenWeatherService() 