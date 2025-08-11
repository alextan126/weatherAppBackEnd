from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.weather import Weather
from app.schemas.weather import WeatherCreate, WeatherUpdate


def get_weather(db: Session, weather_id: int) -> Optional[Weather]:
    return db.query(Weather).filter(Weather.id == weather_id).first()


def get_weather_by_request(db: Session, request_id: int) -> List[Weather]:
    return db.query(Weather).filter(Weather.request_id == request_id).all()


def get_weather_data(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    request_id: Optional[int] = None
) -> List[Weather]:
    query = db.query(Weather)
    if request_id:
        query = query.filter(Weather.request_id == request_id)
    return query.offset(skip).limit(limit).all()


def create_weather(db: Session, weather: WeatherCreate) -> Weather:
    db_weather = Weather(**weather.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather


def update_weather(db: Session, weather_id: int, weather: WeatherUpdate) -> Optional[Weather]:
    db_weather = get_weather(db, weather_id)
    if not db_weather:
        return None
    
    update_data = weather.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_weather, field, value)
    
    db.commit()
    db.refresh(db_weather)
    return db_weather


def delete_weather(db: Session, weather_id: int) -> bool:
    db_weather = get_weather(db, weather_id)
    if not db_weather:
        return False
    
    db.delete(db_weather)
    db.commit()
    return True


def get_weather_by_temperature_range(
    db: Session, 
    min_temp: float, 
    max_temp: float, 
    skip: int = 0, 
    limit: int = 100
) -> List[Weather]:
    return db.query(Weather).filter(
        Weather.temperature >= min_temp,
        Weather.temperature <= max_temp
    ).offset(skip).limit(limit).all()


def get_weather_by_description(db: Session, description: str, skip: int = 0, limit: int = 100) -> List[Weather]:
    return db.query(Weather).filter(Weather.description.contains(description)).offset(skip).limit(limit).all() 