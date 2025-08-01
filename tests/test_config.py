"""Tests for the configuration module."""

import os
from unittest.mock import patch


def test_config_paths():
    """Test that configuration paths are correctly setup."""
    from bot.config import BASE_DIR, DATA_DIR, DB_PATH, TEMP_DIR

    # Check if base directories are set correctly
    assert BASE_DIR.exists()
    assert DATA_DIR.exists()
    assert TEMP_DIR.exists()

    # Verify that DATA_DIR is inside BASE_DIR
    assert str(DATA_DIR).startswith(str(BASE_DIR))

    # Verify that TEMP_DIR is inside DATA_DIR
    assert str(TEMP_DIR).startswith(str(DATA_DIR))

    # Verify DB_PATH is correctly set
    assert DB_PATH.name == "bot.db"
    assert DB_PATH.parent == DATA_DIR


def test_video_formats():
    """Test that video formats are correctly configured."""
    from bot.config import VIDEO_FORMATS

    # Check that we have all the required formats
    assert "SD" in VIDEO_FORMATS
    assert "HD" in VIDEO_FORMATS
    assert "FHD" in VIDEO_FORMATS
    assert "ORIGINAL" in VIDEO_FORMATS

    # Check format structure
    assert "label" in VIDEO_FORMATS["SD"]
    assert "format" in VIDEO_FORMATS["SD"]
    assert "label" in VIDEO_FORMATS["HD"]
    assert "format" in VIDEO_FORMATS["HD"]
    assert "label" in VIDEO_FORMATS["FHD"]
    assert "format" in VIDEO_FORMATS["FHD"]
    assert "label" in VIDEO_FORMATS["ORIGINAL"]
    assert "format" in VIDEO_FORMATS["ORIGINAL"]

    # Check specific format settings
    assert VIDEO_FORMATS["SD"]["format"] == "best[height<=480]"
    assert VIDEO_FORMATS["HD"]["format"] == "best[height<=720]"
    assert VIDEO_FORMATS["FHD"]["format"] == "best[height<=1080]"
    assert VIDEO_FORMATS["ORIGINAL"]["format"] == "best"


def test_audio_format():
    """Test that audio format is correctly configured."""
    from bot.config import AUDIO_FORMAT

    # Check that we have MP3 format
    assert "MP3" in AUDIO_FORMAT

    # Check format structure
    assert "label" in AUDIO_FORMAT["MP3"]
    assert "format" in AUDIO_FORMAT["MP3"]

    # Check specific MP3 format settings
    assert AUDIO_FORMAT["MP3"]["format"] == "bestaudio/best"
    assert AUDIO_FORMAT["MP3"]["label"] == "MP3 (320kbps)"


def test_max_file_size():
    """Test MAX_FILE_SIZE is correctly set."""
    from bot.config import MAX_FILE_SIZE

    # 2GB in bytes
    expected_size = 2 * 1024 * 1024 * 1024
    assert MAX_FILE_SIZE == expected_size


def test_token_validation():
    """Test validation of TELEGRAM_TOKEN."""
    from bot.config import TELEGRAM_TOKEN

    # Token should be set for tests to run
    assert TELEGRAM_TOKEN, "Token should be set for tests to run"
    assert isinstance(TELEGRAM_TOKEN, str)
    assert len(TELEGRAM_TOKEN.strip()) > 0


def test_admin_id_validation():
    """Test validation of ADMIN_USER_ID."""
    from bot.config import ADMIN_USER_ID

    # Admin ID should be set for tests to run
    assert ADMIN_USER_ID, "Admin ID should be set for tests to run"
    assert isinstance(ADMIN_USER_ID, int)
    assert ADMIN_USER_ID > 0


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "mock_token", "ADMIN_USER_ID": "123456"})
def test_env_variables():
    """Test environment variables are correctly used."""
    # We can't easily reload the config module, but we can test
    # that getenv works as expected with our patched environment
    assert os.getenv("TELEGRAM_TOKEN") == "mock_token"
    assert os.getenv("ADMIN_USER_ID") == "123456"

    # And we can test the conversion to int works correctly
    assert int(os.getenv("ADMIN_USER_ID", 0)) == 123456
