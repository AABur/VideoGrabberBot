"""Tests for formats module."""

from bot.services.formats import (
    get_available_formats,
    get_format_by_id,
    get_format_options,
)


class TestFormats:
    """Group tests for the formats module."""

    def test_get_available_formats(
        self, mock_video_formats, mock_audio_formats, clear_format_cache
    ):
        """Test getting available formats with mocked configuration."""
        # First, force a reload of the formats module to ensure
        # it picks up our mocked config values
        import importlib

        import bot.services.formats

        importlib.reload(bot.services.formats)

        # Now get formats
        formats = get_available_formats()

        # Check that we have both video and audio formats
        expected_count = len(mock_video_formats) + len(mock_audio_formats)
        assert len(formats) == expected_count

        # Check that keys are properly prefixed
        for key in formats.keys():
            assert key.startswith("video:") or key.startswith("audio:")

        # Check structure of format data
        for format_data in formats.values():
            assert "label" in format_data
            assert "format" in format_data
            assert "type" in format_data
            assert format_data["type"] in ["video", "audio"]

        # Check specific formats exist with correct data
        for format_id, format_data in mock_video_formats.items():
            key = f"video:{format_id}"
            assert key in formats
            assert formats[key]["label"] == format_data["label"]
            assert formats[key]["format"] == format_data["format"]
            assert formats[key]["type"] == "video"

        for format_id, format_data in mock_audio_formats.items():
            key = f"audio:{format_id}"
            assert key in formats
            assert formats[key]["label"] == format_data["label"]
            assert formats[key]["format"] == format_data["format"]
            assert formats[key]["type"] == "audio"

    def test_get_format_options(
        self, mock_video_formats, mock_audio_formats, clear_format_cache
    ):
        """Test getting format options for inline keyboard."""
        # Reload the module to ensure it picks up our mocked config
        import importlib

        import bot.services.formats

        importlib.reload(bot.services.formats)

        options = get_format_options()

        # Check that options are not empty
        assert len(options) > 0
        assert len(options) == len(mock_video_formats) + len(
            mock_audio_formats
        )

        # Check that each option is a tuple of (callback_data, label)
        for option in options:
            assert len(option) == 2
            assert isinstance(option[0], str)
            assert isinstance(option[1], str)

        # Extract ids and labels
        ids = [opt[0] for opt in options]
        labels = [opt[1] for opt in options]

        # Check that all mocked formats are represented
        for format_id in mock_video_formats.keys():
            assert f"video:{format_id}" in ids

        for format_id in mock_audio_formats.keys():
            assert f"audio:{format_id}" in ids

        # Check that labels match the mocked values
        for format_data in mock_video_formats.values():
            assert format_data["label"] in labels

        for format_data in mock_audio_formats.values():
            assert format_data["label"] in labels

        # Check that video formats come before audio formats
        video_formats = [opt for opt in options if opt[0].startswith("video:")]
        audio_formats = [opt for opt in options if opt[0].startswith("audio:")]

        assert len(video_formats) > 0
        assert len(audio_formats) > 0

        # Get indices of first video and first audio format
        first_video_idx = options.index(video_formats[0])
        first_audio_idx = options.index(audio_formats[0])

        assert first_video_idx < first_audio_idx

    def test_get_format_by_id(
        self, mock_video_formats, mock_audio_formats, clear_format_cache
    ):
        """Test getting format by ID."""
        # Reload the module to ensure it picks up our mocked config
        import importlib

        import bot.services.formats

        importlib.reload(bot.services.formats)

        # Test with valid video format ID
        video_format_id = f"video:{list(mock_video_formats.keys())[0]}"
        format_data = get_format_by_id(video_format_id)
        assert format_data is not None
        assert format_data["type"] == "video"
        original_data = mock_video_formats[video_format_id.split(":")[1]]
        assert format_data["label"] == original_data["label"]
        assert format_data["format"] == original_data["format"]

        # Test with valid audio format ID
        audio_format_id = f"audio:{list(mock_audio_formats.keys())[0]}"
        format_data = get_format_by_id(audio_format_id)
        assert format_data is not None
        assert format_data["type"] == "audio"
        original_data = mock_audio_formats[audio_format_id.split(":")[1]]
        assert format_data["label"] == original_data["label"]
        assert format_data["format"] == original_data["format"]

        # Test with invalid format ID
        format_data = get_format_by_id("invalid:format")
        assert format_data is None

    def test_get_format_by_id_edge_cases(
        self, mock_video_formats, mock_audio_formats, clear_format_cache
    ):
        """Test edge cases for get_format_by_id."""
        # Reload the module to ensure it picks up our mocked config
        import importlib

        import bot.services.formats

        importlib.reload(bot.services.formats)

        # Test with empty string
        format_data = get_format_by_id("")
        assert format_data is None

        # We're using strict typing, so we shouldn't test with None
        # In production code, the type system would prevent this
        # Instead, let's test with another invalid case
        format_data = get_format_by_id("no_colon_here")
        assert format_data is None
