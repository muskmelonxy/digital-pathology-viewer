import os
from pathlib import Path


class Config:
    """Runtime configuration for the Flask application."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://slides_user:slides_pass@postgres:5432/slides_db",
    )

    SLIDE_STORAGE_PATH = os.environ.get("SLIDE_STORAGE_PATH", "/data/slides")

    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ] or ["*"]

    DEEPZOOM_TILE_SIZE = int(os.environ.get("DEEPZOOM_TILE_SIZE", "256"))
    DEEPZOOM_OVERLAP = int(os.environ.get("DEEPZOOM_OVERLAP", "0"))

    @staticmethod
    def ensure_storage_path() -> Path:
        storage_path = Path(Config.SLIDE_STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path
