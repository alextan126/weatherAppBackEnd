from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.weather import Weather
from typing import List

router = APIRouter()

@router.get("/weather/", response_model=List[dict])
async def get_weather_data(db: Session = Depends(get_db)):
    """Get all weather data"""
    weather_data = db.query(Weather).all()
    return [
        {
            "id": w.id,
            "location": w.location,
            "temperature": w.temperature,
            "humidity": w.humidity,
            "pressure": w.pressure,
            "wind_speed": w.wind_speed,
            "wind_direction": w.wind_direction,
            "description": w.description,
            "icon": w.icon,
            "created_at": w.created_at
        }
        for w in weather_data
    ]

@router.get("/weather/{location}")
async def get_weather_by_location(location: str, db: Session = Depends(get_db)):
    """Get weather data for a specific location"""
    weather = db.query(Weather).filter(Weather.location == location).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return {
        "id": weather.id,
        "location": weather.location,
        "temperature": weather.temperature,
        "humidity": weather.humidity,
        "pressure": weather.pressure,
        "wind_speed": weather.wind_speed,
        "wind_direction": weather.wind_direction,
        "description": weather.description,
        "icon": weather.icon,
        "created_at": weather.created_at
    }

@router.post("/weather/")
async def create_weather_data(
    location: str,
    temperature: float = None,
    humidity: float = None,
    pressure: float = None,
    wind_speed: float = None,
    wind_direction: float = None,
    description: str = None,
    icon: str = None,
    db: Session = Depends(get_db)
):
    """Create new weather data"""
    weather = Weather(
        location=location,
        temperature=temperature,
        humidity=humidity,
        pressure=pressure,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        description=description,
        icon=icon
    )
    db.add(weather)
    db.commit()
    db.refresh(weather)
    
    return {
        "id": weather.id,
        "location": weather.location,
        "temperature": weather.temperature,
        "humidity": weather.humidity,
        "pressure": weather.pressure,
        "wind_speed": weather.wind_speed,
        "wind_direction": weather.wind_direction,
        "description": weather.description,
        "icon": weather.icon,
        "created_at": weather.created_at
    } 