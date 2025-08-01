# bot/services/storage.py
"""Temporary storage for handling URL data."""

import time
import uuid
from typing import Dict, Optional, Tuple

# URL_STORAGE format: {url_id: (url, format_id, timestamp)}
URL_STORAGE: Dict[str, Tuple[str, Optional[str], float]] = {}

# TTL configuration
TTL_SECONDS = 3600  # 1 hour
MAX_STORAGE_SIZE = 1000  # Maximum number of entries


def _cleanup_expired_entries() -> None:
    """Remove expired entries from storage."""
    current_time = time.time()
    expired_keys = [key for key, (_, _, timestamp) in URL_STORAGE.items() if current_time - timestamp > TTL_SECONDS]
    for key in expired_keys:
        URL_STORAGE.pop(key, None)


def _enforce_size_limit() -> None:
    """Enforce maximum storage size by removing oldest entries."""
    if len(URL_STORAGE) <= MAX_STORAGE_SIZE:
        return

    # Sort by timestamp and keep only the newest entries
    sorted_items = sorted(URL_STORAGE.items(), key=lambda x: x[1][2], reverse=True)
    URL_STORAGE.clear()
    for key, item_value in sorted_items[:MAX_STORAGE_SIZE]:
        URL_STORAGE[key] = item_value


def store_url(url: str) -> str:
    """
    Store URL in temporary storage and return unique ID.

    Args:
        url: URL to store

    Returns:
        Unique ID for the URL
    """
    _cleanup_expired_entries()
    _enforce_size_limit()

    url_id = str(uuid.uuid4())[:8]  # Short UUID
    URL_STORAGE[url_id] = (url, None, time.time())
    return url_id


def get_url(url_id: str) -> Optional[str]:
    """
    Get URL by ID.

    Args:
        url_id: URL ID

    Returns:
        URL or None if not found
    """
    _cleanup_expired_entries()
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
    _cleanup_expired_entries()
    existing_data = URL_STORAGE.get(url_id)
    if existing_data is None:
        return False

    url, _, timestamp = existing_data
    URL_STORAGE[url_id] = (url, format_id, timestamp)
    return True


def get_format(url_id: str) -> Optional[str]:
    """
    Get format ID for URL.

    Args:
        url_id: URL ID

    Returns:
        Format ID or None if not found
    """
    _cleanup_expired_entries()
    format_data = URL_STORAGE.get(url_id)
    return format_data[1] if format_data else None


def clear_url(url_id: str) -> None:
    """
    Remove URL from storage.

    Args:
        url_id: URL ID
    """
    URL_STORAGE.pop(url_id, None)
