"""Format handling module for VideoGrabberBot."""

from typing import Dict, List, Tuple

from bot.config import AUDIO_FORMAT, VIDEO_FORMATS


def get_available_formats(url: str = None) -> Dict[str, Dict[str, str]]:
    """
    Get available formats for the URL.

    Args:
        url: URL of the video (optional)

    Returns:
        Dict of format types and their details.
    """
    # For now, we return all configured formats
    # In the future, this can be extended to filter formats based on URL or video properties
    formats = {}

    # Add video formats
    for format_id, format_data in VIDEO_FORMATS.items():
        formats[f"video:{format_id}"] = {
            "label": format_data["label"],
            "format": format_data["format"],
            "type": "video",
        }

    # Add audio formats
    for format_id, format_data in AUDIO_FORMAT.items():
        formats[f"audio:{format_id}"] = {
            "label": format_data["label"],
            "format": format_data["format"],
            "type": "audio",
        }

    return formats


def get_format_options() -> List[Tuple[str, str]]:
    """
    Get format options for InlineKeyboard.

    Returns:
        List of (callback_data, label) tuples for InlineKeyboard buttons.
    """
    formats = get_available_formats()
    options = []

    # Add video formats first
    for format_id, format_data in formats.items():
        if format_data["type"] == "video":
            options.append((format_id, format_data["label"]))

    # Then add audio formats
    for format_id, format_data in formats.items():
        if format_data["type"] == "audio":
            options.append((format_id, format_data["label"]))

    return options


def get_format_by_id(format_id: str) -> Dict[str, str]:
    """
    Get format details by format ID.

    Args:
        format_id: Format ID in the format 'type:format' (e.g., 'video:HD')

    Returns:
        Format details dict or None if not found
    """
    formats = get_available_formats()
    return formats.get(format_id)
