"""Tests for the storage module."""

from bot.services.storage import (
    clear_url,
    get_format,
    get_url,
    store_format,
    store_url,
)


def test_url_storage():
    """Test storing and retrieving URLs."""
    # Store a URL
    url = "https://www.youtube.com/watch?v=test"
    url_id = store_url(url)

    # Check that ID is a string
    assert isinstance(url_id, str)
    assert len(url_id) == 8  # Short UUID

    # Retrieve URL
    retrieved_url = get_url(url_id)
    assert retrieved_url == url

    # Store format
    format_id = "video:HD"
    result = store_format(url_id, format_id)
    assert result is True

    # Retrieve format
    retrieved_format = get_format(url_id)
    assert retrieved_format == format_id

    # Clear URL
    clear_url(url_id)

    # Verify URL was cleared
    assert get_url(url_id) is None
    assert get_format(url_id) is None


def test_nonexistent_url():
    """Test retrieving nonexistent URL."""
    assert get_url("nonexistent") is None
    assert get_format("nonexistent") is None
    assert store_format("nonexistent", "video:HD") is False

    # Clear should not raise error
    clear_url("nonexistent")
