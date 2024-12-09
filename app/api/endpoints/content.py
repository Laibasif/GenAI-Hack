from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.news_service import NewsService
from app.services.meme_generator import MemeGenerator
from app.services.text_generator import TextGenerator
from app.services.image_generator import ImageGenerator
from fastapi.responses import HTMLResponse
import google.generativeai as genai

import os

# Import the ContentGenerator class
from app.utils.content_generator import ContentGenerator


router = APIRouter(prefix="", tags=["content"])

# Initialize ContentGenerator with your credentials
TAVUS_API_KEY = 'b2c0cbb7e3484d2496c1c766f49acf5b'  # Replace with your actual Tavus API key
IMGFLIP_USERNAME = 'ManuAdam'
IMGFLIP_PASSWORD = 'Cyberme@50'

content_generator = ContentGenerator(TAVUS_API_KEY, IMGFLIP_USERNAME, IMGFLIP_PASSWORD)

@router.get("/", response_class=HTMLResponse)
async def get_html():
    with open("templates/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.post("/")
async def generate_content(
    content_type: str = Query(..., description="Type of content to generate: 'meme', 'video', or 'text'"),
    category: Optional[str] = None,
    query: Optional[str] = None,
    tone: Optional[str] = "professional",
    format: Optional[str] = "social_media",
    # Meme-specific params
    template_id='181913649',
    top_text='When you use APIs',
    bottom_text='When you do everything manually',
    output_path: str = Query("/content/meme.jpg", description="Path to save the generated meme"),
    # Video-specific params
    replica_id: Optional[str] = 'r79e1c033f',
    background_url: Optional[str] = Query("", description="Optional background URL"),
    video_name: Optional[str] = Query("generated_video", description="Name for the generated video")
):
    """
    Generate content dynamically based on the provided content_type.
    Supported types: 'meme', 'video', 'text'.
    """
    try:
    
        # Initialize NewsService
        news_service = NewsService()

        # Fetch news articles
        news_data = await news_service.fetch_news(category, query)
        if not news_data.get("news"):
            raise HTTPException(status_code=404, detail="No news articles found")

        # Summarize the first article
        article = news_data["news"][0]
        summary = await news_service.summarize_article(
            title=article.get("title", "Untitled"),
            content=article.get("text", "No content available"),
            tone=tone,
            format=format
        )

        if content_type == "text" or content_type == "post":
            # If content type is text, return the summarized article
            return {
                "original_article": article,
                "generated_summary": summary,
                "content_type": "text"
            }

        elif content_type == "meme":
            # # Use the summarized content as meme text
            # top_text = "Summary of News"
            # bottom_text = summary
            meme_service = MemeGenerator()
            meme = meme_service.create_meme(
                template_id,
                content=summary,  # Pass the summarized news as content
                tone=tone         # Pass the selected tone
            )
            # meme_path = meme_service.create_meme(
            #     template_id=template_id,
            #     top_text=top_text,
            #     bottom_text=bottom_text
            # )
            if meme:
                return {"message": "Meme generated successfully", "meme_path": meme}
            else:
                raise HTTPException(status_code=500, detail="Meme generation failed")

        elif content_type == "video":
            # Use the summarized content as the script for the video
            video_response = content_generator.generate_video_with_tavus(
                script=summary,
                replica_id=replica_id,
                background_url=background_url,
                video_name=video_name
            )
            if video_response:
                return {"message": "Video generation successful", "video_response": video_response}
            else:
                raise HTTPException(status_code=500, detail="Video generation failed")

        else:
            raise HTTPException(status_code=400, detail="Unsupported content type. Use 'meme', 'video', or 'text'.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
