from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Content Generator"
    API_V1_STR: str = "/api/v1"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    IMGFLIP_USERNAME: Optional[str] = None
    IMGFLIP_PASSWORD: Optional[str] = None
    SYNTHESIA_API_KEY: Optional[str] = None
    
    # News API Settings
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()