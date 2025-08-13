from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.routes import weather, locations
from app.db.session import get_db

app = FastAPI(title="Weather API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather.router)
app.include_router(locations.router)

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