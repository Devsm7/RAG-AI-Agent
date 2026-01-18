"""
Environment variables and configuration
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
load_dotenv()  

class Config:
    """Application configuration"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    DATASETS_DIR = PROJECT_ROOT / "datasets"
    CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
    STATIC_DIR = PROJECT_ROOT / "static"
    MODELS_DIR = PROJECT_ROOT / "models"
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8080"))
    
    # Model settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "medium")
    
    # OpenAI settings (for Arabic responses)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Whisper settings
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    
    # Retrieval settings
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "20"))  # Increased to retrieve more documents
    
    # Database files
    BOOTCAMPS_CSV: Path = DATASETS_DIR / "bootcamps_new.csv"
    PLACES_CSV: Path = DATASETS_DIR / "places_new.csv"
    REVIEWS_CSV: Path = DATASETS_DIR / "reviews.csv"


config = Config()
