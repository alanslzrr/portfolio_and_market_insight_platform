"""Centralized configuration for the Streamlit frontend."""
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


@dataclass
class Settings:
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    debug: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    page_title: str = "Portfolio & Market Insight"
    page_icon: str = "chart"
    layout: str = "wide"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
