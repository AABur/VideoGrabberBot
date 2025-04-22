"""Base fixtures for VideoGrabberBot tests."""

import asyncio
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset URL storage between tests.
    
    This fixture automatically runs before and after each test
    to prevent test interference through shared state.
    """
    from bot.services.storage import URL_STORAGE
    
    # Save original storage
    original_storage = URL_STORAGE.copy()
    
    # Clear storage before test
    URL_STORAGE.clear()
    
    yield
    
    # Clear and restore storage after test
    URL_STORAGE.clear()
    URL_STORAGE.update(original_storage)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session.
    
    This fixture ensures a consistent event loop for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_video_formats():
    """Mock video formats for testing.
    
    Provides consistent test formats independent of the actual configuration.
    """
    test_formats = {
        "TEST_SD": {"label": "Test SD (480p)", "format": "test[height<=480]"},
        "TEST_HD": {"label": "Test HD (720p)", "format": "test[height<=720]"},
        "TEST_FHD": {"label": "Test Full HD (1080p)", "format": "test[height<=1080]"},
        "TEST_ORIGINAL": {"label": "Test Original", "format": "test"},
    }
    
    with patch("bot.config.VIDEO_FORMATS", test_formats):
        yield test_formats


@pytest.fixture
def mock_audio_formats():
    """Mock audio formats for testing.
    
    Provides consistent test formats independent of the actual configuration.
    """
    test_formats = {
        "TEST_MP3": {"label": "Test MP3 (320kbps)", "format": "testaudio"}
    }
    
    with patch("bot.config.AUDIO_FORMAT", test_formats):
        yield test_formats


@pytest.fixture
def clear_format_cache():
    """Clear format cache if it exists.
    
    This is a future-proofing fixture that will help if lru_cache
    is added to formats.py in the future.
    """
    # Currently the functions in formats.py don't use lru_cache
    # If they do in the future, we'll need to clear the cache here
    
    yield
    
    # After test, attempt to clear caches if they exist
    try:
        from bot.services.formats import get_available_formats, get_format_options
        
        for func in [get_available_formats, get_format_options]:
            if hasattr(func, "cache_clear"):
                func.cache_clear()
    except (ImportError, AttributeError):
        # If the functions don't exist or don't have cache_clear, it's okay
        pass
