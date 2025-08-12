from sqlalchemy.orm import Session
from app.db.base_class import Base
from app.models.user import User
from app.models.request import Request
from app.models.weather import Weather
from app.core.security import get_password_hash
# app/models/__init__.py
from .location import Location
from .weather_observation import WeatherObservation
from .weather_request import WeatherRequest

def init_db(db: Session) -> None:
    """Initialize database with seed data"""
    
    # Check if we already have data
    user = db.query(User).first()
    if user:
        return
    
    # Create initial user
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True
    )
    db.add(user)
    
    # Commit the changes
    db.commit()
    print("Database initialized with seed data")

if __name__ == "__main__":
    from app.db.session import SessionLocal
    db = SessionLocal()
    init_db(db)
    db.close()
