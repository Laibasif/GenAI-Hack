from openai import AsyncOpenAI
from app.core.config import settings
from fastapi import HTTPException

class ImageGenerator:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
