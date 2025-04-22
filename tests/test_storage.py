"""Tests for the storage module."""

from bot.services.storage import (
    clear_url,
    get_format,
    get_url,
    store_format,
    store_url,
)


class TestStorage:
    """Test class for the storage module functions."""

    def test_url_storage_lifecycle(self):
        """Test the full lifecycle of URL storage: store, get, update, clear."""
        # Store a URL and verify it returns a valid ID
        url = "https://www.youtube.com/watch?v=test123"
        url_id = store_url(url)

        # Verify ID properties
        assert isinstance(url_id, str)
        assert len(url_id) == 8  # Should be a short UUID

        # Retrieve URL and verify it matches
        retrieved_url = get_url(url_id)
        assert retrieved_url == url

        # Verify format is initially None
        assert get_format(url_id) is None

        # Store format and verify success
        format_id = "video:TEST_HD"
        result = store_format(url_id, format_id)
        assert result is True

        # Retrieve format and verify
        retrieved_format = get_format(url_id)
        assert retrieved_format == format_id

        # Clear URL and verify it's gone
        clear_url(url_id)
        assert get_url(url_id) is None
        assert get_format(url_id) is None

    def test_multiple_urls(self):
        """Test handling multiple URLs simultaneously."""
        # Store multiple URLs
        url1 = "https://www.youtube.com/watch?v=test1"
        url2 = "https://www.youtube.com/watch?v=test2"

        url_id1 = store_url(url1)
        url_id2 = store_url(url2)

        # Verify they're different IDs
        assert url_id1 != url_id2

        # Verify correct URLs are retrieved
        assert get_url(url_id1) == url1
        assert get_url(url_id2) == url2

        # Store formats
        store_format(url_id1, "video:TEST_SD")
        store_format(url_id2, "audio:TEST_MP3")

        # Verify formats
        assert get_format(url_id1) == "video:TEST_SD"
        assert get_format(url_id2) == "audio:TEST_MP3"

        # Clear one URL
        clear_url(url_id1)

        # Verify first URL is gone but second remains
        assert get_url(url_id1) is None
        assert get_format(url_id1) is None
        assert get_url(url_id2) == url2
        assert get_format(url_id2) == "audio:TEST_MP3"

        # Clean up second URL
        clear_url(url_id2)

    def test_nonexistent_url(self):
        """Test operations on nonexistent URLs."""
        # Generate a random ID that shouldn't exist
        nonexistent_id = "nonexist"

        # Try to get a nonexistent URL
        assert get_url(nonexistent_id) is None
        assert get_format(nonexistent_id) is None

        # Try to store a format for nonexistent URL
        result = store_format(nonexistent_id, "video:TEST_HD")
        assert result is False

        # Clear nonexistent URL should not raise errors
        clear_url(nonexistent_id)  # Should not raise

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Empty URL
        url_id = store_url("")
        assert isinstance(url_id, str)
        assert get_url(url_id) == ""
        clear_url(url_id)

        # Empty format ID
        url_id = store_url("https://example.com")
        assert store_format(url_id, "") is True
        assert get_format(url_id) == ""
        clear_url(url_id)

        # For invalid URL IDs (we're not testing None as that's handled by type checking)
        assert get_url("non_existent_id") is None
        assert store_format("non_existent_id", "some_format") is False
        assert get_format("non_existent_id") is None
