from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.session import get_db
from app.models.weather import Location, WeatherObservation
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi.responses import JSONResponse

router = APIRouter(tags=["weather"])

class APIResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None

def ok(data: Any = None, meta: Optional[Dict[str, Any]] = None):
    """Standard success envelope"""
    return {"success": True, "data": data, "meta": meta}

def fail(status_code: int, code: str, message: str, meta: Optional[Dict[str, Any]] = None):
    """Standard error envelope (returns a JSONResponse)"""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}, "meta": meta},
    )

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
#TODO: Missing the data collection logic: 
#User search the db, if db doesn't have the data, send API
#to fill the data and return the data from db. not supported right now because OpenWeather Free Tier no usable.

@router.post("/weather/query")
async def create_weather_query(
    request: WeatherCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a weather query and return stored hourly temperatures in range.
    start_ts and end_ts must be ISO 8601 datetime strings (e.g., YYYY-MM-DDTHH:MM:SSZ)."""
    
    if request.start_ts >= request.end_ts:
        return fail(400, "INVALID_RANGE", "start_ts must be before end_ts")
    
    # Fuzzy search for location
    location = db.query(Location).filter(
        func.lower(Location.name).contains(func.lower(request.q))
    ).first()
    
    if not location:
        return fail(404, "LOCATION_NOT_FOUND", "Location not found")
    
    # Get observations in range
    observations = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location.id,
            WeatherObservation.ts >= request.start_ts,
            WeatherObservation.ts <= request.end_ts
        )
    ).all()
    
    return ok({
        "location": {
            "id": location.id,
            "name": location.name,
            "country": location.country,
            "admin1": location.admin1,
            "latitude": location.latitude,
            "longitude": location.longitude
        },
        "range": {"start_ts": request.start_ts, "end_ts": request.end_ts},
        "observations": [
            {"ts": obs.ts, "temp_c": obs.temp_c, "source": obs.source}
            for obs in observations
        ]
    })

@router.get("/weather/observations")
async def get_weather_observations(
    location_id: Optional[int] = Query(
        None,
        description="Numeric ID of the location (optional if q_fuzzy_location is provided)"
    ),
    q_fuzzy_location: Optional[str] = Query(
        None,
        description="Fuzzy search term for location name (optional if location_id is provided)"
    ),
    start_ts: datetime = Query(
        ...,
        description="Start of date/time range in strict ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"
    ),
    end_ts: datetime = Query(
        ...,
        description="End of date/time range in strict ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"
    ),
    db: Session = Depends(get_db)
):
    """Read observations in the specified range.
    start_ts and end_ts must be ISO 8601 datetime strings (e.g., YYYY-MM-DDTHH:MM:SSZ)."""
    if not location_id and not q_fuzzy_location:
        return fail(400, "MISSING_LOCATION_SELECTOR", "Either location_id or q_fuzzy_location must be provided")
    
    if location_id:
        location = db.query(Location).filter(Location.id == location_id).first()
    else:
        location = db.query(Location).filter(
            func.lower(Location.name).contains(func.lower(q_fuzzy_location))
        ).first()
    
    if not location:
        return fail(404, "LOCATION_NOT_FOUND", "Location not found")
    
    observations = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location.id,
            WeatherObservation.ts >= start_ts,
            WeatherObservation.ts <= end_ts
        )
    ).all()
    
    return ok({
        "location": {
            "id": location.id,
            "name": location.name,
            "country": location.country,
            "admin1": location.admin1,
            "latitude": location.latitude,
            "longitude": location.longitude
        },
        "range": {"start_ts": start_ts, "end_ts": end_ts},
        "observations": [
            {"ts": obs.ts, "temp_c": obs.temp_c, "source": obs.source}
            for obs in observations
        ]
    })

"""
Batch Upsert Weather Observations Endpoint

Purpose:
This endpoint allows batch insertion or updating of weather observations for a specific location.
It accepts multiple observations in a single request and performs an upsert operation:
- Inserts new rows if they do not exist.
- Updates existing rows if they have the same location_id and timestamp.

Request Body Format (JSON):
{
    "location_id": <integer>,
    "observations": [
        {
            "ts": "<ISO 8601 datetime string>",
            "temp_c": <float>,
            "source": "<optional string>"
        },
        ...
    ]
}

Example Request Payload:
{
    "location_id": 123,
    "observations": [
        {"ts": "2024-06-01T12:00:00Z", "temp_c": 22.5, "source": "sensorA"},
        {"ts": "2024-06-01T13:00:00Z", "temp_c": 23.0}
    ]
}

"""

@router.post("/weather/observations/upsert")
async def upsert_weather_observations(
    request: ObservationUpsertRequest,
    db: Session = Depends(get_db)
):
    """Batch upsert observations using PostgreSQL ON CONFLICT"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == request.location_id).first()
    if not location:
        return fail(404, "LOCATION_NOT_FOUND", "Location not found")
    
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
    
    return ok({
        "location_id": request.location_id,
        "upserted": len(request.observations)
    })

@router.put("/weather/observations/CreateOne")
async def update_single_observation(
    request: ObservationUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a single observation"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == request.location_id).first()
    if not location:
        return fail(404, "LOCATION_NOT_FOUND", "Location not found")
    
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
    
    return ok({
        "id": observation.id,
        "location_id": observation.location_id,
        "ts": observation.ts,
        "temp_c": observation.temp_c,
        "source": observation.source
    })

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
        return fail(404, "LOCATION_NOT_FOUND", "Location not found")
    
    # Delete observations in range
    deleted_count = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location_id,
            WeatherObservation.ts >= start_ts,
            WeatherObservation.ts <= end_ts
        )
    ).delete()
    
    db.commit()
    
    return ok({
        "location_id": location_id,
        "range": {"start_ts": start_ts, "end_ts": end_ts},
        "deleted": deleted_count
    })