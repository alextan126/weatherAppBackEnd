# Weather API Backend

A FastAPI backend application for weather data management with PostgreSQL database.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker (optional, for database)

### Option A: Local PostgreSQL Setup(Not Recomended)

1. **Install PostgreSQL:**

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql

   # Windows: Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database:**

   ```bash
   createdb weather_db
   createuser -P weather  # Set password when prompted
   ```

3. **Install Python Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run Database Migrations:**

   ```bash
   alembic upgrade head
   ```

6. **Start the Application:**
   ```bash
   python run.py
   ```

### Option B: Docker Setup (Recomended)

1. **Start PostgreSQL with Docker:**

   ```bash
   docker run --name weather-postgres \
     -e POSTGRES_USER=weather \
     -e POSTGRES_PASSWORD=weather123 \
     -e POSTGRES_DB=weather_db \
     -p 5432:5432 \
     -d postgres:15
   ```

2. **Install Python Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables:**

   ```bash
   cp .env.example .env
   # Edit .env with Docker database credentials
   ```

4. **Run DB Migrations/ Deploy DB schema:**

   ```bash
   alembic upgrade head
   ```

5. **Start the Application:**
   ```bash
   python run.py
   ```

## API Endpoints

### Weather Endpoints

- `POST /api/v1/weather/query` - Query weather data by location and time range
- `GET /api/v1/weather/observations` - Get weather observations
- `POST /api/v1/weather/observations/upsert` - Batch upsert observations
- `PUT /api/v1/weather/observations/CreateOne` - Create/update single observation
- `DELETE /api/v1/weather/observations` - Delete observations in range

### Location Endpoints

- `GET /api/v1/locations/search` - Search locations
- `POST /api/v1/locations/create` - Create new location

### Health Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /db-health` - Database connectivity check

## Configuration

### Environment Variables

```bash
DB_USER=weather
DB_PASS=weather123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather_db
API_V1_STR=/api/v1
PROJECT_NAME=Weather API
```

### Database Schema

- **locations**: Location information (name, country, coordinates)
- **weather_observations**: Weather data points (timestamp, temperature, source)

## 🧪 Testing

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/db-health

# Query weather data
curl -X POST "http://localhost:8000/api/v1/weather/query" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "San Francisco",
    "start_ts": "2025-01-01T00:00:00Z",
    "end_ts": "2025-01-02T00:00:00Z"
  }'
```

### Test with Python

```python
import requests

# Test the API
response = requests.get("http://localhost:8000/health")
print(response.json())
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed:**

   - Check if PostgreSQL is running
   - Verify credentials in .env file
   - Ensure database exists

2. **Port Already in Use:**

   - Change port in run.py or kill existing process
   - `lsof -ti:8000 | xargs kill -9`

3. **Import Errors:**
   - Ensure you're in the backend directory
   - Check Python path: `export PYTHONPATH=$PYTHONPATH:$(pwd)`

### Logs

Check application logs for detailed error information.

## Project Structure
