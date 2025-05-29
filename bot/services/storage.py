# bot/services/storage.py
"""Temporary storage for handling URL data."""

import uuid
from typing import Any, Dict, Optional

# URL_STORAGE format: {url_id: (url, format_id)}
URL_STORAGE: Dict[str, Any] = {}


def store_url(url: str) -> str:
    """
    Store URL in temporary storage and return unique ID.

    Args:
        url: URL to store

    Returns:
        Unique ID for the URL
    """
    url_id = str(uuid.uuid4())[:8]  # Short UUID
    URL_STORAGE[url_id] = (url, None)
    return url_id


def get_url(url_id: str) -> Optional[str]:
    """
    Get URL by ID.

    Args:
        url_id: URL ID

    Returns:
        URL or None if not found
    """
    url_data = URL_STORAGE.get(url_id)
    return url_data[0] if url_data else None


def store_format(url_id: str, format_id: str) -> bool:
    """
    Store format ID for URL.

    Args:
        url_id: URL ID
        format_id: Format ID

    Returns:
        True if success, False if URL not found
    """
    existing_data = URL_STORAGE.get(url_id)
    if existing_data is None:
        return False

    url = existing_data[0]
    URL_STORAGE[url_id] = (url, format_id)
    return True


def get_format(url_id: str) -> Optional[str]:
    """
    Get format ID for URL.

    Args:
        url_id: URL ID

    Returns:
        Format ID or None if not found
    """
    format_data = URL_STORAGE.get(url_id)
    return format_data[1] if format_data else None


def clear_url(url_id: str) -> None:
    """
    Remove URL from storage.

    Args:
        url_id: URL ID
    """
    URL_STORAGE.pop(url_id, None)
