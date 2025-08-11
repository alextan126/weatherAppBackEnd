from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class WeatherBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    forecast_date: Optional[datetime] = None


class WeatherCreate(WeatherBase):
    request_id: int
    raw_data: Optional[Dict[str, Any]] = None


class WeatherUpdate(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    forecast_date: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None


class WeatherInDBBase(WeatherBase):
    id: int
    request_id: int
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Weather(WeatherInDBBase):
    pass


class WeatherInDB(WeatherInDBBase):
    pass 