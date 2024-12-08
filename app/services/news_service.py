import httpx
from app.core.config import settings
from fastapi import HTTPException
import google.generativeai as genai


class NewsService:
    def __init__(self):
        # if not settings.NEWS_API_KEY:
        #     raise HTTPException(status_code=500, detail="News API key not configured")
        # if not settings.GENAI_API_KEY:
        #     raise HTTPException(status_code=500, detail="Generative AI API key not configured")
        NEWS_API_KEY = "9d8d3ea474424f75b4ffc00c8ddd3931"  # Replace with your actual news API key
        NEWS_BASE_URL = "https://api.worldnewsapi.com/search-news"
        self.base_url = NEWS_BASE_URL
        self.api_key = NEWS_API_KEY
        GENAI_API_KEY = "AIzaSyAnfEvhg0Uz6Oahgvyoyy1FLGIWKzd6LhI"  # Replace with your actual Gemini API key
        genai.configure(api_key=GENAI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure model availability for your API key

    async def fetch_news(self, category: str, query: str, language: str = "en") -> dict:
        """
        Fetches news articles from the API based on the query and category.
        """
        params = {
            "api-key": self.api_key,
            "text": query,
            "language": language,
            "category": category,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                news_data = response.json()
                return news_data
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {e}")

    async def summarize_article(self, title: str, content: str, tone: str, format: str) -> str:
        """
        Summarizes a news article using the Generative AI model.
        """
        prompt = (
            f"You are an AI assistant specialized in summarizing news articles.\n"
            f"Tone: {tone}\n"
            f"Format: {format}\n"
            f"Title: {title}\n"
            f"Content: {content}\n"
            "Provide a concise and engaging summary."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error summarizing article: {e}")
