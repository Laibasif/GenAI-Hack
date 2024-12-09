import httpx
import logging
from fastapi import HTTPException
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class NewsService:
    def __init__(self):
        # NewsData.io API Configuration
        self.api_key = "pub_6184107e7288c957d2a39e067dcfc74b3f461"  # Replace with your actual NewsData.io API key
        self.base_url = "https://newsdata.io/api/1/news"

        # Gemini API Configuration
        genai_api_key = "AIzaSyAnfEvhg0Uz6Oahgvyoyy1FLGIWKzd6LhI"  # Replace with your actual Gemini API key
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure model availability for your API key

    async def fetch_news(self, category: str, query: str, language: str = "en") -> dict:
        """
        Fetches news articles from the NewsData.io API based on the query and category.
        """
        params = {
            "apikey": self.api_key,  # API key for authentication
            "q": query,             # Search query
            "language": language,   # Language filter (e.g., 'en' for English)
            # "category": category    # Category filter (e.g., 'technology', 'health')
        }

        logging.info(f"Fetching news for category: {category}, query: {query}, language: {language}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                news_data = response.json()
                if 'results' in news_data and news_data['results']:
                    logging.info(f"Fetched {len(news_data['results'])} articles from NewsData.io")
                else:
                    logging.warning("No articles found in the API response.")
                return {"news": news_data.get("results", [])}  # Return articles in a consistent structure
        except httpx.RequestError as e:
            logging.error(f"Error fetching news: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error while fetching news: {e}")
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

        logging.info(f"Generating summary for article titled '{title}' with tone '{tone}' and format '{format}'.")
        
        try:
            response = self.model.generate_content(prompt)
            logging.info(f"Summarization successful for title: '{title}'")
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error summarizing article '{title}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error summarizing article: {e}")