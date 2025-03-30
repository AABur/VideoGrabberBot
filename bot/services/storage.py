# bot/services/storage.py
"""Temporary storage for handling URL data."""

import uuid
from typing import Dict, Optional, Tuple

# URL_STORAGE format: {url_id: (url, format_id)}
URL_STORAGE: Dict[str, Tuple[str, Optional[str]]] = {}


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
    data = URL_STORAGE.get(url_id)
    if data:
        return data[0]
    return None


def store_format(url_id: str, format_id: str) -> bool:
    """
    Store format ID for URL.

    Args:
        url_id: URL ID
        format_id: Format ID

    Returns:
        True if success, False if URL not found
    """
    if url_id in URL_STORAGE:
        url = URL_STORAGE[url_id][0]
        URL_STORAGE[url_id] = (url, format_id)
        return True
    return False


def get_format(url_id: str) -> Optional[str]:
    """
    Get format ID for URL.

    Args:
        url_id: URL ID

    Returns:
        Format ID or None if not found
    """
    data = URL_STORAGE.get(url_id)
    if data:
        return data[1]
    return None


def clear_url(url_id: str) -> None:
    """
    Remove URL from storage.

    Args:
        url_id: URL ID
    """
    if url_id in URL_STORAGE:
        del URL_STORAGE[url_id]
