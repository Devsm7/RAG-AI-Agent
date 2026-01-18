"""
Health check endpoint
"""
from fastapi import APIRouter
from twuaqirag.core.config import config

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_english": config.LLM_MODEL,
        "model_arabic": config.GEMINI_MODEL if config.GOOGLE_API_KEY else config.LLM_MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "google_api_configured": bool(config.GOOGLE_API_KEY)
    }
