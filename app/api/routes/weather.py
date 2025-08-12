from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.session import get_db
from app.models.weather import Location, WeatherObservation
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class WeatherCreateRequest(BaseModel):
    q: str
    start_ts: datetime
    end_ts: datetime

class ObservationUpsertRequest(BaseModel):
    location_id: int
    observations: List[dict]  # [{ts, temp_c, source?}, ...]

class ObservationUpdateRequest(BaseModel):
    location_id: int
    ts: datetime
    temp_c: float
    source: Optional[str] = None

class LocationSearchResponse(BaseModel):
    id: int
    name: str
    country: Optional[str]
    admin1: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

@router.post("/weather/create")
async def create_weather_query(
    request: WeatherCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a weather query and return stored hourly temperatures in range"""
    # Validate date range
    if request.start_ts >= request.end_ts:
        raise HTTPException(status_code=400, detail="start_ts must be before end_ts")
    
    # Fuzzy search for location
    location = db.query(Location).filter(
        func.lower(Location.name).contains(func.lower(request.q))
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get observations in range
    observations = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location.id,
            WeatherObservation.ts >= request.start_ts,
            WeatherObservation.ts <= request.end_ts
        )
    ).all()
    
    return {
        "location": location.name,
        "location_id": location.id,
        "start_ts": request.start_ts,
        "end_ts": request.end_ts,
        "observations": [
            {
                "ts": obs.ts,
                "temp_c": obs.temp_c,
                "source": obs.source
            }
            for obs in observations
        ]
    }

@router.get("/weather/observations")
async def get_weather_observations(
    location_id: Optional[int] = None,
    q: Optional[str] = None,
    start_ts: datetime = Query(...),
    end_ts: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Read observations in the specified range"""
    if not location_id and not q:
        raise HTTPException(status_code=400, detail="Either location_id or q must be provided")
    
    if location_id:
        location = db.query(Location).filter(Location.id == location_id).first()
    else:
        location = db.query(Location).filter(
            func.lower(Location.name).contains(func.lower(q))
        ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    observations = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location.id,
            WeatherObservation.ts >= start_ts,
            WeatherObservation.ts <= end_ts
        )
    ).all()
    
    return {
        "location": location.name,
        "location_id": location.id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "observations": [
            {
                "ts": obs.ts,
                "temp_c": obs.temp_c,
                "source": obs.source
            }
            for obs in observations
        ]
    }

@router.post("/weather/observations/upsert")
async def upsert_weather_observations(
    request: ObservationUpsertRequest,
    db: Session = Depends(get_db)
):
    """Batch upsert observations using PostgreSQL ON CONFLICT"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == request.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Prepare observations for upsert
    for obs_data in request.observations:
        observation = WeatherObservation(
            location_id=request.location_id,
            ts=obs_data["ts"],
            temp_c=obs_data["temp_c"],
            source=obs_data.get("source")
        )
        
        # Use merge for upsert behavior
        db.merge(observation)
    
    db.commit()
    
    return {"message": f"Upserted {len(request.observations)} observations", "location_id": request.location_id}

@router.put("/weather/observations/one")
async def update_single_observation(
    request: ObservationUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a single observation"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == request.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Find existing observation
    observation = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == request.location_id,
            WeatherObservation.ts == request.ts
        )
    ).first()
    
    if observation:
        # Update existing
        observation.temp_c = request.temp_c
        observation.source = request.source
    else:
        # Create new
        observation = WeatherObservation(
            location_id=request.location_id,
            ts=request.ts,
            temp_c=request.temp_c,
            source=request.source
        )
        db.add(observation)
    
    db.commit()
    db.refresh(observation)
    
    return {
        "id": observation.id,
        "location_id": observation.location_id,
        "ts": observation.ts,
        "temp_c": observation.temp_c,
        "source": observation.source
    }

@router.delete("/weather/observations")
async def delete_weather_observations(
    location_id: int,
    start_ts: datetime = Query(...),
    end_ts: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Delete observations in the specified range"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Delete observations in range
    deleted_count = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location_id,
            WeatherObservation.ts >= start_ts,
            WeatherObservation.ts <= end_ts
        )
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} observations",
        "location_id": location_id,
        "start_ts": start_ts,
        "end_ts": end_ts
    } 