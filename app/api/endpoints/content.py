from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.news_service import NewsService
from app.services.text_generator import TextGenerator
from app.services.image_generator import ImageGenerator

router = APIRouter(prefix="/content", tags=["content"])

@router.post("/generate")
async def generate_content(
    category: Optional[str] = None,
    query: Optional[str] = None,
    content_type: str = "text",
    tone: str = "professional",
    format: str = "social_media"
):
    try:
        # Initialize services
        news_service = NewsService()
        text_generator = TextGenerator()
        image_generator = ImageGenerator()

        # Fetch news
        news_data = await news_service.fetch_news(category, query)
        if not news_data.get("articles"):
            raise HTTPException(status_code=404, detail="No news articles found")

        # Generate content based on type
        article = news_data["articles"][0]
        
        if content_type == "text":
            content = await text_generator.generate_summary(
                article["description"],
                tone,
                format
            )
        elif content_type == "image":
            content = await image_generator.generate_image(
                article["description"],
                tone
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported content type")

        return {
            "original_article": article,
            "generated_content": content,
            "content_type": content_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
