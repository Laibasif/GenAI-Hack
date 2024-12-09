from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import news, content, auth
from app.api.endpoints.auth import router as auth_router
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(news.router)
app.include_router(content.router)
