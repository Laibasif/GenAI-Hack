import httpx
from app.core.config import settings
from fastapi import HTTPException

class NewsService:
    def __init__(self):
        if not settings.NEWS_API_KEY:
            raise HTTPException(status_code=500, detail="News API key not configured")
        self.base_url = settings.NEWS_API_BASE_URL
        self.api_key = settings.NEWS_API_KEY
