"""Configuration module for VideoGrabberBot."""

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram configuration
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in .env file")

ADMIN_USER_ID: int = int(os.getenv("ADMIN_USER_ID", 0))
if not ADMIN_USER_ID:
    raise ValueError("ADMIN_USER_ID is not set in .env file")

# File system paths
BASE_DIR: Path = Path(__file__).parent.parent.absolute()
DATA_DIR: Path = BASE_DIR / "data"
TEMP_DIR: Path = DATA_DIR / "temp"
DB_PATH: Path = DATA_DIR / "bot.db"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Download configuration
MAX_FILE_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB
VIDEO_FORMATS: Dict[str, Dict[str, str]] = {
    "SD": {"label": "SD (480p)", "format": "best[height<=480]"},
    "HD": {"label": "HD (720p)", "format": "best[height<=720]"},
    "FHD": {"label": "Full HD (1080p)", "format": "best[height<=1080]"},
    "ORIGINAL": {"label": "Original (Max Quality)", "format": "best"},
}
AUDIO_FORMAT: Dict[str, Dict[str, str]] = {
    "MP3": {"label": "MP3 (320kbps)", "format": "bestaudio/best"}
}
