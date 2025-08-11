from fastapi import APIRouter
from app.api.routes import weather

api_router = APIRouter()

# Include all route modules
api_router.include_router(weather.router, prefix="/weather", tags=["weather"]) 