from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.weather import Location
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(tags=["locations"])

class LocationSearchResponse(BaseModel):
    id: int
    name: str
    country: Optional[str]
    admin1: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class LocationCreateRequest(BaseModel):
    name: str
    country: Optional[str] = None
    admin1: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@router.get("/locations/search", response_model=List[LocationSearchResponse])
async def search_locations(
    q: str = Query(..., description="Search query for location name"),
    country: Optional[str] = Query(None, description="Filter by country"),
    admin1: Optional[str] = Query(None, description="Filter by state/province"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Fuzzy search locations using pg_trgm similarity"""
    query = db.query(Location)
    
    # Basic text search
    if q:
        query = query.filter(
            func.lower(Location.name).contains(func.lower(q))
        )
    
    # Apply filters
    if country:
        query = query.filter(func.lower(Location.country) == func.lower(country))
    
    if admin1:
        query = query.filter(func.lower(Location.admin1) == func.lower(admin1))
    
    # Limit results
    locations = query.limit(limit).all()
    
    return [
        LocationSearchResponse(
            id=loc.id,
            name=loc.name,
            country=loc.country,
            admin1=loc.admin1,
            latitude=loc.latitude,
            longitude=loc.longitude
        )
        for loc in locations
    ]

@router.post("/locations/create")
async def create_location(
    data: LocationCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new location"""
    # Check if location already exists
    existing = db.query(Location).filter(
        func.lower(Location.name) == func.lower(data.name)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Location already exists")
    
    location = Location(
        name=data.name,
        country=data.country,
        admin1=data.admin1,
        latitude=data.latitude,
        longitude=data.longitude
    )
    
    db.add(location)
    db.commit()
    db.refresh(location)
    
    return {
        "id": location.id,
        "name": location.name,
        "country": location.country,
        "admin1": location.admin1,
        "latitude": location.latitude,
        "longitude": location.longitude
    } 