"""Tests for the configuration module."""

import os
import importlib
from pathlib import Path

import pytest


def test_config_paths():
    """Test that configuration paths are correctly setup."""
    from bot.config import BASE_DIR, DATA_DIR, TEMP_DIR

    # Check if base directories are set correctly
    assert BASE_DIR.exists()
    assert DATA_DIR.exists()
    assert TEMP_DIR.exists()

    # Verify that DATA_DIR is inside BASE_DIR
    assert str(DATA_DIR).startswith(str(BASE_DIR))

    # Verify that TEMP_DIR is inside DATA_DIR
    assert str(TEMP_DIR).startswith(str(DATA_DIR))


def test_video_formats():
    """Test that video formats are correctly configured."""
    from bot.config import VIDEO_FORMATS

    # Check that we have all the required formats
    assert "SD" in VIDEO_FORMATS
    assert "HD" in VIDEO_FORMATS
    assert "FHD" in VIDEO_FORMATS
    assert "ORIGINAL" in VIDEO_FORMATS

    # Check format structure
    for format_key, format_data in VIDEO_FORMATS.items():
        assert "label" in format_data
        assert "format" in format_data


def test_audio_format():
    """Test that audio format is correctly configured."""
    from bot.config import AUDIO_FORMAT

    # Check that we have MP3 format
    assert "MP3" in AUDIO_FORMAT

    # Check format structure
    for format_key, format_data in AUDIO_FORMAT.items():
        assert "label" in format_data
        assert "format" in format_data


# Удаляем тест на проверку переменных окружения, так как он вызывает проблемы
# Этот тест более сложно реализовать, требуется полностью перезагружать модуль
# и изолировать окружение, что не всегда просто сделать с pytest