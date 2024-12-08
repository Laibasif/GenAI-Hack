from fastapi import APIRouter

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/")
async def get_news():
    return {"message": "News endpoint"}
