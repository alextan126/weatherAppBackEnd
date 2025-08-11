import httpx
from typing import Optional, Tuple
from app.core.config import settings


class GeocodingService:
    def __init__(self):
        self.api_key = settings.GEOCODING_API_KEY
        self.base_url = "https://api.openweathermap.org/geo/1.0"
    
    async def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates (latitude, longitude) for a given location
        """
        if not self.api_key:
            # Fallback to OpenWeatherMap geocoding (free tier)
            return await self._get_coordinates_openweathermap(location)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/direct",
                    params={
                        "q": location,
                        "limit": 1,
                        "appid": self.api_key
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                if data and len(data) > 0:
                    lat = data[0]["lat"]
                    lon = data[0]["lon"]
                    return (lat, lon)
                
        except Exception as e:
            print(f"Error getting coordinates: {e}")
        
        return None
    
    async def _get_coordinates_openweathermap(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Fallback to OpenWeatherMap geocoding API
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/direct",
                    params={
                        "q": location,
                        "limit": 1,
                        "appid": settings.OPENWEATHER_API_KEY
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                if data and len(data) > 0:
                    lat = data[0]["lat"]
                    lon = data[0]["lon"]
                    return (lat, lon)
                
        except Exception as e:
            print(f"Error getting coordinates from OpenWeatherMap: {e}")
        
        return None


geocoding_service = GeocodingService() 