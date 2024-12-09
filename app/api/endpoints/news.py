from fastapi import APIRouter, Query
import requests
import google.generativeai as genai
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
)

router = APIRouter(prefix="/news", tags=["news"])

# NewsData.io API Configuration
NEWS_API_KEY = "pub_6184107e7288c957d2a39e067dcfc74b3f461"  # Replace with your actual NewsData.io API key
NEWS_BASE_URL = "https://newsdata.io/api/1/news"

# Gemini API Configuration
GENAI_API_KEY = "AIzaSyAnfEvhg0Uz6Oahgvyoyy1FLGIWKzd6LhI"  # Replace with your actual Gemini API key
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure this model is available for your API key

@router.get("/")
async def get_news(
    keyword: str = Query(..., description="Keyword to search news articles"), 
    tone: str = Query("formal", description="Tone for summarization (e.g., formal, conversational)")
):
    """
    Fetches and summarizes news articles based on user input.
    """
    logging.info(f"Fetching news for keyword: {keyword} with tone: {tone}")
    
    # Fetch articles
    articles = fetch_news(NEWS_API_KEY, keyword=keyword, language="en")
    
    if articles:
        logging.info(f"Found {len(articles)} articles. Processing summaries...")
        responses = process_articles(articles, content_type="LinkedIn post", tone=tone)
        logging.info("Summarization completed successfully.")
        return {"message": "News fetched and summarized successfully.", "articles": responses}
    else:
        logging.warning(f"No articles found for keyword: {keyword}")
        return {"message": "No articles found for the provided keyword.", "articles": []}

def fetch_news(api_key, keyword, language='en'):
    """
    Fetches news articles based on the keyword and language using NewsData.io API.
    """
    params = {
        "apikey": api_key,
        "q": keyword,
        "language": language,
    }
    url = NEWS_BASE_URL + "?" + urlencode(params)
    logging.info(f"Making request to NewsData.io API: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (non-200 status codes)
        news_data = response.json()
        logging.info(f"API response received with status code {response.status_code}")

        if 'results' in news_data and news_data['results']:
            logging.info(f"Fetched {len(news_data['results'])} articles from NewsData.io")
            return news_data['results']  # Use 'results' field as per NewsData.io's response structure
        else:
            logging.warning("No results found in the API response.")
            return []

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return []

def summarize_with_gemini(title, content, content_type, tone):
    """
    Summarizes the content of a news article using the Gemini API.
    """
    prompt = (
        f"You are an AI assistant specialized in summarizing news articles.\n"
        f"Content type: {content_type}\n"
        f"Tone: {tone}\n"
        f"Title: {title}\n"
        f"Content: {content}\n"
        "Please provide a summarized version of the article in the specified tone."
    )
    
    logging.debug(f"Summarization prompt created for title: '{title}'")
    
    try:
        response = model.generate_content(prompt)
        logging.info(f"Summarization successful for title: '{title}'")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error summarizing the article '{title}': {str(e)}")
        return f"Error summarizing the article: {str(e)}"

def process_articles(articles, content_type, tone):
    """
    Processes and summarizes a list of articles.
    """
    list_of_summaries = []
    
    for idx, article in enumerate(articles[:5]):  # Limit to 5 articles for brevity
        title = article.get("title", "No Title")
        content = article.get("description", "No Content")  # Use 'description' from NewsData.io
        
        logging.info(f"Processing article {idx + 1}: '{title}'")
        
        summary = summarize_with_gemini(
            title=title,
            content=content,
            content_type=content_type,
            tone=tone,
        )
        
        news = {
            "title": title,
            "summary": summary,
            "author": article.get("source_id", "Unknown Author"),  # Use 'source_id' as author placeholder
            "url": article.get("link", "No URL Provided"),  # Use 'link' from NewsData.io for article URL
        }
        
        list_of_summaries.append(news)
    
    logging.info("All articles processed successfully.")
    
    return list_of_summaries