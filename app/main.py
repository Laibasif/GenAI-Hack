from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import news, content, auth
from app.api.endpoints.auth import router as auth_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(news.router, prefix=settings.API_V1_STR)
app.include_router(content.router, prefix=settings.API_V1_STR)
