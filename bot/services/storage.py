# bot/services/storage.py
"""Temporary storage for handling URL data."""

import time
import uuid
from typing import Dict, Optional, Tuple

from bot.config import config


class UrlStorage:
    """Thread-safe in-memory storage for URL data with TTL and size limits."""

    def __init__(self) -> None:
        """Initialize URL storage."""
        # Internal data format: {url_id: (url, format_id, timestamp)}
        self._data: Dict[str, Tuple[str, Optional[str], float]] = {}

    def _cleanup_expired_entries(self) -> None:
        """Remove expired entries from storage."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, _, timestamp) in self._data.items() if current_time - timestamp > config.TTL_SECONDS
        ]
        for key in expired_keys:
            self._data.pop(key, None)

    def _enforce_size_limit(self) -> None:
        """Enforce maximum storage size by removing oldest entries."""
        if len(self._data) <= config.MAX_STORAGE_SIZE:
            return

        # Sort by timestamp and keep only the newest entries
        sorted_items = sorted(self._data.items(), key=lambda x: x[1][2], reverse=True)
        self._data.clear()
        for key, item_value in sorted_items[: config.MAX_STORAGE_SIZE]:
            self._data[key] = item_value

    def _get_storage_data(self, url_id: str, index: int) -> Optional[str]:
        """Get data from storage by URL ID and tuple index.

        Args:
            url_id: URL ID
            index: Index in storage tuple (0=url, 1=format_id)

        Returns:
            Data at specified index or None if not found
        """
        self._cleanup_expired_entries()
        storage_data = self._data.get(url_id)
        if storage_data:
            value = storage_data[index]
            return value if isinstance(value, str) else None
        return None

    def store_url(self, url: str) -> str:
        """
        Store URL in temporary storage and return unique ID.

        Args:
            url: URL to store

        Returns:
            Unique ID for the URL
        """
        self._cleanup_expired_entries()
        self._enforce_size_limit()

        url_id = str(uuid.uuid4())[:8]  # Short UUID
        self._data[url_id] = (url, None, time.time())
        return url_id

    def get_url(self, url_id: str) -> Optional[str]:
        """
        Get URL by ID.

        Args:
            url_id: URL ID

        Returns:
            URL or None if not found
        """
        return self._get_storage_data(url_id, 0)

    def store_format(self, url_id: str, format_id: str) -> bool:
        """
        Store format ID for URL.

        Args:
            url_id: URL ID
            format_id: Format ID

        Returns:
            True if success, False if URL not found
        """
        self._cleanup_expired_entries()
        existing_data = self._data.get(url_id)
        if existing_data is None:
            return False

        url, _, timestamp = existing_data
        self._data[url_id] = (url, format_id, timestamp)
        return True

    def get_format(self, url_id: str) -> Optional[str]:
        """
        Get format ID for URL.

        Args:
            url_id: URL ID

        Returns:
            Format ID or None if not found
        """
        return self._get_storage_data(url_id, 1)

    def clear_url(self, url_id: str) -> None:
        """
        Remove URL from storage.

        Args:
            url_id: URL ID
        """
        self._data.pop(url_id, None)


# Module-level instance for backward compatibility
url_storage = UrlStorage()

# Backward-compatible alias: references the internal dict directly so that
# existing code using URL_STORAGE[key] / URL_STORAGE.get(key) still works.
URL_STORAGE = url_storage._data


# Backward-compatible module-level functions
def store_url(url: str) -> str:
    """Store URL in temporary storage and return unique ID."""
    return url_storage.store_url(url)


def get_url(url_id: str) -> Optional[str]:
    """Get URL by ID."""
    return url_storage.get_url(url_id)


def store_format(url_id: str, format_id: str) -> bool:
    """Store format ID for URL."""
    return url_storage.store_format(url_id, format_id)


def get_format(url_id: str) -> Optional[str]:
    """Get format ID for URL."""
    return url_storage.get_format(url_id)


def clear_url(url_id: str) -> None:
    """Remove URL from storage."""
    url_storage.clear_url(url_id)
