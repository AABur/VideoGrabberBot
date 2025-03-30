"""Tests for formats module."""

from bot.services.formats import (
    get_available_formats,
    get_format_by_id,
    get_format_options,
)


def test_get_available_formats():
    """Test getting available formats."""
    formats = get_available_formats()

    # Check that we have both video and audio formats
    assert len(formats) > 0

    # Check that keys are properly prefixed
    for key in formats.keys():
        assert key.startswith("video:") or key.startswith("audio:")

    # Check structure of format data
    for format_data in formats.values():
        assert "label" in format_data
        assert "format" in format_data
        assert "type" in format_data
        assert format_data["type"] in ["video", "audio"]


def test_get_format_options():
    """Test getting format options for inline keyboard."""
    options = get_format_options()

    assert len(options) > 0

    # Check that each option is a tuple of (callback_data, label)
    for option in options:
        assert len(option) == 2
        assert isinstance(option[0], str)
        assert isinstance(option[1], str)

    # Check that video formats come before audio formats
    video_formats = [opt for opt in options if opt[0].startswith("video:")]
    audio_formats = [opt for opt in options if opt[0].startswith("audio:")]

    assert len(video_formats) > 0
    assert len(audio_formats) > 0

    # Get indices of first video and first audio format
    first_video_idx = options.index(video_formats[0])
    first_audio_idx = options.index(audio_formats[0])

    assert first_video_idx < first_audio_idx


def test_get_format_by_id():
    """Test getting format by ID."""
    # Test with valid format ID
    format_data = get_format_by_id("video:HD")
    assert format_data is not None
    assert format_data["type"] == "video"
    assert "HD" in format_data["label"]

    # Test with valid audio format ID
    format_data = get_format_by_id("audio:MP3")
    assert format_data is not None
    assert format_data["type"] == "audio"
    assert "MP3" in format_data["label"]

    # Test with invalid format ID
    format_data = get_format_by_id("invalid:format")
    assert format_data is None
