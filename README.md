# Weather API - Minimal Skeleton

A simple FastAPI application for weather data management.

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**

   ```bash
   DATABASE_URL=postgresql://user:password@localhost/weatherdb
   API_V1_STR=/api/v1
   PROJECT_NAME=Weather API
   ```

3. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - DB Health check
- `GET /api/v1/weather/` - Get all weather data
- `GET /api/v1/weather/{location}` - Get weather by location
- `POST /api/v1/weather/` - Create weather data

## Database

The app uses PostgreSQL with a simple Weather model containing:

- Location
- Temperature, humidity, pressure
- Wind speed and direction
- Description and icon
- Timestamp

## Development

This is a minimal skeleton with:

- FastAPI backend
- SQLAlchemy ORM
- Basic CRUD operations
- No authentication
- No complex business logic

Add features as needed!
