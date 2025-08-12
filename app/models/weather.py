from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    country = Column(String, nullable=True)
    admin1 = Column(String, nullable=True)  # State/province
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)  # timestamp
    temp_c = Column(Float, nullable=False)  # temperature in Celsius
    source = Column(String, nullable=True)  # data source
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="observations")

# Add relationship to Location
Location.observations = relationship("WeatherObservation", back_populates="location")