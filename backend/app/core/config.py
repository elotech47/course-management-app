from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql://user:password@localhost:5432/course_management")
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY","your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
    
    # Email
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY",None)
    FROM_EMAIL: str = os.getenv("FROM_EMAIL","noreply@example.com")
    FROM_NAME: str = os.getenv("FROM_NAME","Course Management System")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL","redis://localhost:6379/0")
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT","development")
    DEBUG: bool = os.getenv("DEBUG",True)

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
