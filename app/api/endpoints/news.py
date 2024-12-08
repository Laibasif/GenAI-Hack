from fastapi import APIRouter, Query
import requests
import google.generativeai as genai
from urllib.parse import urlencode

router = APIRouter(prefix="/news", tags=["news"])
NEWS_API_KEY = "5c79806ac8d3477b843ffb4f52292802"  # Replace with your actual news API key
NEWS_BASE_URL = "https://api.worldnewsapi.com/search-news"

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
    # Fetch articles
    articles = fetch_news(NEWS_API_KEY, keyword=keyword, language="en")
    
    if articles:
        responses = process_articles(articles, content_type="LinkedIn post", tone=tone)
        return {"message": "News fetched and summarized successfully.", "articles": responses}
    else:
        return {"message": "No articles found for the provided keyword.", "articles": []}

def fetch_news(api_key, keyword, language='en'):
    """
    Fetches news articles based on the keyword and language.
    """
    params = {
        "api-key": api_key,
        "text": keyword,
        "language": language,
    }
    url = NEWS_BASE_URL + "?" + urlencode(params)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (non-200 status codes)
        news_data = response.json()

        if 'news' in news_data and news_data['news']:
            return news_data['news']
        else:
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
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

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error summarizing the article: {str(e)}"

def process_articles(articles, content_type, tone):
    """
    Processes and summarizes a list of articles.
    """
    list_of_summaries = []
    for article in articles[:5]:  # Limit to 5 articles for brevity
        summary = summarize_with_gemini(
            title=article.get("title", "No Title"), 
            content=article.get("text", "No Content"), 
            content_type=content_type, 
            tone=tone
        )
        news = {
            "title": article.get("title", "No Title"),
            "summary": summary,
            "author": article.get("author", "Unknown Author"),
            "url": article.get("url", "No URL Provided")
        }
        list_of_summaries.append(news)
    return list_of_summaries
