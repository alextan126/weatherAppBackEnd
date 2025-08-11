from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/weatherdb"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Weather API"
    
    class Config:
        env_file = ".env"

settings = Settings() 