from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

"""
Hourly weather schema with normalized locations.
- Location: canonical place info (name, region, lat/lon)
- WeatherObservation: hourly temperature per location (UTC), composite PK (location_id, ts)

NOTE: Table partitioning by year will be added via Alembic raw SQL; the ORM
model below represents only the parent table.
"""
from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Float,
    DateTime,
    Numeric,
    PrimaryKeyConstraint,
    func,
)
from app.db.session import Base


class Location(Base):
    __tablename__ = "location"

    location_id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, nullable=False)            # e.g., "San Francisco"
    country_code = Column(Text)                    # ISO-2 like 'US'
    admin1 = Column(Text)                          # state/province, e.g., 'CA'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    external_source = Column(Text)                 # optional (e.g., 'geocoder')
    external_id = Column(Text)                     # optional stable external id
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class WeatherObservation(Base):
    __tablename__ = "weather_observation"

    # Composite PK: (location_id, ts)
    location_id = Column(BigInteger, nullable=False, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)   # hourly timestamp (UTC)
    temp_c = Column(Numeric(5, 2), nullable=False)                     # temperature in Celsius
    source = Column(Text)                                              # e.g., 'NOAA', 'ERA5'
    inserted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("location_id", "ts", name="pk_weather_observation"),
    )