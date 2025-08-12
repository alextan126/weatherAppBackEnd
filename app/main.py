from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, text, and_
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.weather import Location, WeatherObservation

# Create the FastAPI app
app = FastAPI(title="Weather API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UpsertObservationsIn(BaseModel):
    location_id: int
    observations: List[dict]

class UpdateObservationIn(BaseModel):
    location_id: int
    ts: str
    temp_c: float
    source: Optional[str] = None

# -----------------------------
# CREATE: external data; it returns whatever is already stored for that range.
# -----------------------------
@app.post("/api/v1/weather/create")
def create_request(
    q: str = Query(..., description="Free‑text location (e.g., 'San Fran')"),
    start_ts: str = Query(..., description="Start timestamp (ISO format)"),
    end_ts: str = Query(..., description="End timestamp (ISO format)"),
    db: Session = Depends(get_db)
):
    # Validate date range
    try:
        start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="start_ts must be before end_ts")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Fuzzy search for location
    location = db.query(Location).filter(
        func.lower(Location.name).contains(func.lower(q))
    ).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get observations in range
    observations = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location.id,
            WeatherObservation.ts >= start_dt,
            WeatherObservation.ts <= end_dt
        )
    ).all()
    
    return {
        "location": location.name,
        "location_id": location.id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "observations": [
            {
                "ts": obs.ts.isoformat(),
                "temp_c": obs.temp_c,
                "source": obs.source
            }
            for obs in observations
        ]
    }

# -----------------------------
# READ: by location (id or free‑text) and date range
# -----------------------------
@app.get("/api/v1/weather/observations")
def read_observations(
    location_id: Optional[int] = Query(None),
    q: Optional[str] = Query(None),
    start_ts: str = Query(..., description="Start timestamp (ISO format)"),
    end_ts: str = Query(..., description="End timestamp (ISO format)"),
    db: Session = Depends(get_db)
):
    if not location_id and not q:
        raise HTTPException(status_code=400, detail="Either location_id or q must be provided")
    
    try:
        start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
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
            WeatherObservation.ts >= start_dt,
            WeatherObservation.ts <= end_dt
        )
    ).all()
    
    return {
        "location": location.name,
        "location_id": location.id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "observations": [
            {
                "ts": obs.ts.isoformat(),
                "temp_c": obs.temp_c,
                "source": obs.source
            }
            for obs in observations
        ]
    }

# -----------------------------
# UPDATE: upsert (insert or update) a batch of hourly readings
# -----------------------------
@app.post("/api/v1/weather/observations/upsert")
def upsert_observations(payload: UpsertObservationsIn, db: Session = Depends(get_db)):
    if not payload.observations:
        raise HTTPException(status_code=400, detail="No observations provided")
    
    # Verify location exists
    location = db.query(Location).filter(Location.id == payload.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Prepare observations for upsert
    for obs_data in payload.observations:
        try:
            ts = datetime.fromisoformat(obs_data["ts"].replace('Z', '+00:00'))
        except (ValueError, KeyError):
            raise HTTPException(status_code=400, detail="Invalid timestamp in observations")
        
        observation = WeatherObservation(
            location_id=payload.location_id,
            ts=ts,
            temp_c=obs_data["temp_c"],
            source=obs_data.get("source")
        )
        
        # Use merge for upsert behavior
        db.merge(observation)
    
    db.commit()
    
    return {"message": f"Upserted {len(payload.observations)} observations", "location_id": payload.location_id}

# -----------------------------
# UPDATE: update a single observation (manual correction)
# -----------------------------
@app.put("/api/v1/weather/observations/one")
def update_one(payload: UpdateObservationIn, db: Session = Depends(get_db)):
    # Reuse upsert to avoid duplicate code
    upsert_payload = UpsertObservationsIn(
        location_id=payload.location_id,
        observations=[{
            "ts": payload.ts,
            "temp_c": payload.temp_c,
            "source": payload.source
        }]
    )
    return upsert_observations(upsert_payload, db)

# -----------------------------
# DELETE: delete observations by location and date range
# -----------------------------
@app.delete("/api/v1/weather/observations")
def delete_observations(
    location_id: int = Query(...),
    start_ts: str = Query(..., description="Start timestamp (ISO format)"),
    end_ts: str = Query(..., description="End timestamp (ISO format)"),
    db: Session = Depends(get_db)
):
    try:
        start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Verify location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Delete observations in range
    deleted_count = db.query(WeatherObservation).filter(
        and_(
            WeatherObservation.location_id == location_id,
            WeatherObservation.ts >= start_dt,
            WeatherObservation.ts <= end_dt
        )
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} observations",
        "location_id": location_id,
        "start_ts": start_ts,
        "end_ts": end_ts
    }

# -----------------------------
# Utility: fuzzy search endpoint to help clients resolve locations
# -----------------------------
@app.get("/api/v1/locations/search")
def search_locations(
    q: str = Query(..., description="Search query for location name"),
    country: Optional[str] = Query(None, description="Filter by country"),
    admin1: Optional[str] = Query(None, description="Filter by state/province"),
    limit: int = Query(5, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    stmt = db.query(Location)
    
    # Basic text search
    if q:
        stmt = stmt.filter(func.lower(Location.name).contains(func.lower(q)))
    
    # Apply filters
    if country:
        stmt = stmt.filter(func.lower(Location.country) == func.lower(country))
    
    if admin1:
        stmt = stmt.filter(func.lower(Location.admin1) == func.lower(admin1))
    
    # Limit results
    locations = stmt.limit(limit).all()
    
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "country": loc.country,
            "admin1": loc.admin1,
            "latitude": loc.latitude,
            "longitude": loc.longitude
        }
        for loc in locations
    ]

# Add missing imports and basic endpoints

@app.get("/")
async def root():
    return {"message": "Weather API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-health")
async def db_health(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"database": "connected", "result": result}
    except Exception as e:
        return {"database": "error", "details": str(e)}