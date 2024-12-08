from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/")
async def auth_status():
    return {"message": "Auth endpoint"}
