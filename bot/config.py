"""Configuration module for VideoGrabberBot."""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def validate_token(token: str) -> str:
    """Validate the Telegram token.

    Args:
        token: Telegram bot token to validate.

    Returns:
        The token if valid.

    Raises:
        ValueError: If token is empty.
    """
    if not token:
        raise ValueError("TELEGRAM_TOKEN is not set in .env file")
    return token


def validate_admin_id(admin_id: int) -> int:
    """Validate the admin user ID.

    Args:
        admin_id: Telegram admin user ID to validate.

    Returns:
        The admin ID if valid.

    Raises:
        ValueError: If admin ID is zero.
    """
    if not admin_id:
        raise ValueError("ADMIN_USER_ID is not set in .env file")
    return admin_id


# Telegram configuration
TELEGRAM_TOKEN: str = validate_token(os.getenv("TELEGRAM_TOKEN", ""))
ADMIN_USER_ID: int = validate_admin_id(int(os.getenv("ADMIN_USER_ID", 0)))

# Web configuration
WEBHOOK_HOST: Optional[str] = os.getenv("WEBHOOK_HOST", None)
WEBHOOK_PATH: str = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL: Optional[str] = None
if WEBHOOK_HOST:
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT: int = int(os.getenv("PORT", 10000))

# Determine if we should use webhook or polling
# We detect if we're running on Render.com by checking for their environment directory
IS_RENDER: bool = os.path.exists("/opt/render")
USE_WEBHOOK: bool = bool(WEBHOOK_HOST) or IS_RENDER

# File system paths
BASE_DIR: Path = Path(__file__).parent.parent.absolute()
# Use mounted disk on Render if available, otherwise use default data directory
DATA_DIR: Path = Path("/data") if os.path.exists("/data") else BASE_DIR / "data"
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
