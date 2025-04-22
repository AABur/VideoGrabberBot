"""Base fixtures for VideoGrabberBot tests.

This module contains common fixtures used across all test modules to ensure
proper isolation and consistent behavior of tests regardless of execution order.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset URL storage between tests.

    This fixture automatically runs before and after each test
    to prevent test interference through shared state.

    Importance:
    - Critical for test isolation
    - Prevents side effects between tests
    - Maintains consistency regardless of test order

    Implementation details:
    - Saves the original URL_STORAGE state
    - Clears the storage before each test
    - Restores the original state after each test
    - Uses autouse=True to run automatically for all tests

    Usage:
    - No explicit import needed (autouse)
    - Applied to all tests automatically
    - Can be overridden by isolated_url_storage for more aggressive isolation
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


# NOTE: We don't need to define our own event_loop fixture anymore.
# pytest-asyncio provides this fixture, and we should use the marking instead.
# For example: @pytest.mark.asyncio(scope="session")
#
# The following was causing a deprecation warning:
#
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an event loop for the test session."""
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     asyncio.set_event_loop(loop)
#     yield loop
#     loop.close()


@pytest.fixture
def mock_video_formats():
    """Mock video formats for testing.

    Provides consistent test formats independent of the actual configuration.
    This ensures tests don't rely on the actual configuration values which
    might change over time.
    """
    test_formats = {
        "TEST_SD": {"label": "Test SD (480p)", "format": "test[height<=480]"},
        "TEST_HD": {"label": "Test HD (720p)", "format": "test[height<=720]"},
        "TEST_FHD": {
            "label": "Test Full HD (1080p)",
            "format": "test[height<=1080]",
        },
        "TEST_ORIGINAL": {"label": "Test Original", "format": "test"},
    }

    # Use import and then patch the imported module's attribute
    # This ensures the patch affects all code accessing the value
    import bot.config

    original_formats = bot.config.VIDEO_FORMATS
    bot.config.VIDEO_FORMATS = test_formats

    yield test_formats

    # Restore the original formats
    bot.config.VIDEO_FORMATS = original_formats


@pytest.fixture
def mock_audio_formats():
    """Mock audio formats for testing.

    Provides consistent test formats independent of the actual configuration.
    This ensures tests don't rely on the actual configuration values which
    might change over time.
    """
    test_formats = {
        "TEST_MP3": {"label": "Test MP3 (320kbps)", "format": "testaudio"}
    }

    # Use import and then patch the imported module's attribute
    # This ensures the patch affects all code accessing the value
    import bot.config

    original_formats = bot.config.AUDIO_FORMAT
    bot.config.AUDIO_FORMAT = test_formats

    yield test_formats

    # Restore the original formats
    bot.config.AUDIO_FORMAT = original_formats


@pytest.fixture(autouse=True)
def clear_format_cache():
    """Clear function caches in the formats module between tests.

    This fixture prevents cached values from causing test interference,
    especially for functions decorated with @lru_cache.

    Importance:
    - Essential for consistent test results
    - Prevents cached values from leaking between tests
    - Ensures each test runs with fresh function caches
    - Particularly important when mocking configuration values

    Implementation details:
    - Called before and after each test
    - Safely identifies and clears caches of format-related functions
    - Uses hasattr() to check if the function has a cache to clear
    - Handles import errors gracefully (for when modules are being mocked)
    - Uses autouse=True to run automatically for all tests

    Usage:
    - No explicit import needed (autouse)
    - Works especially well with test configurations that modify formats
    - Use in combination with the mock_video_formats and mock_audio_formats fixtures

    Common issues:
    - Tests failing only when run together but passing individually
    - Unexpected format values appearing in tests
    - Mock configurations not being respected
    """
    # Before test, try to clear format caches if they exist
    try:
        from bot.services.formats import (
            get_available_formats,
            get_format_by_id,
            get_format_options,
        )

        for func in [
            get_available_formats,
            get_format_options,
            get_format_by_id,
        ]:
            if hasattr(func, "cache_clear"):
                func.cache_clear()
    except (ImportError, AttributeError):
        # If the functions don't exist or don't have cache_clear, it's okay
        pass

    yield

    # After test, try to clear caches again
    try:
        from bot.services.formats import (
            get_available_formats,
            get_format_by_id,
            get_format_options,
        )

        for func in [
            get_available_formats,
            get_format_options,
            get_format_by_id,
        ]:
            if hasattr(func, "cache_clear"):
                func.cache_clear()
    except (ImportError, AttributeError):
        pass


@pytest.fixture
def mock_config():
    """Mock configuration variables for testing.

    This provides a controlled environment for tests by mocking
    global configuration values that may affect test outcomes.

    Returns:
        Dict containing all mocked configuration values for reference
    """
    test_config = {
        "TELEGRAM_TOKEN": "test_token",
        "ADMIN_USER_ID": 12345,
        "MAX_QUEUE_SIZE": 5,
        "DOWNLOAD_TIMEOUT": 300,
        "MAX_FILESIZE": 50 * 1024 * 1024,  # 50MB for tests
        "TEMP_DIR": "test_temp_dir",
        "DB_PATH": "memory:test_db",  # Use in-memory DB for isolation
    }

    # Create a context manager that patches multiple config variables
    with (
        patch("bot.config.TELEGRAM_TOKEN", test_config["TELEGRAM_TOKEN"]),
        patch("bot.config.ADMIN_USER_ID", test_config["ADMIN_USER_ID"]),
        patch("bot.config.MAX_QUEUE_SIZE", test_config["MAX_QUEUE_SIZE"]),
        patch("bot.config.DOWNLOAD_TIMEOUT", test_config["DOWNLOAD_TIMEOUT"]),
        patch("bot.config.MAX_FILESIZE", test_config["MAX_FILESIZE"]),
        patch("bot.config.TEMP_DIR", test_config["TEMP_DIR"]),
        patch("bot.config.DB_PATH", test_config["DB_PATH"]),
    ):
        yield test_config


@pytest.fixture
def mock_telegram_user(user_id: int = 12345):
    """Create a mock Telegram user.

    Args:
        user_id: Telegram user ID (defaults to admin user ID)

    Returns:
        Mock User object
    """
    from aiogram.types import User

    user = MagicMock(spec=User)
    user.id = user_id
    user.username = f"test_user_{user_id}"
    user.first_name = "Test"
    user.last_name = "User"

    return user


@pytest.fixture
def mock_telegram_message(mock_telegram_user):
    """Create a mock Telegram message.

    Args:
        mock_telegram_user: Mock user fixture

    Returns:
        Mock Message object
    """
    from aiogram.types import Message

    message = MagicMock(spec=Message)
    message.from_user = mock_telegram_user
    message.chat.id = mock_telegram_user.id
    message.text = "Test message"
    message.answer = AsyncMock()
    message.reply = AsyncMock()

    return message


@pytest.fixture
def authorized_user_mock():
    """Mock the user authorization check to return True.

    This fixture patches the is_user_authorized function to always return True.
    """
    with patch(
        "bot.handlers.download.is_user_authorized",
        AsyncMock(return_value=True),
    ):
        yield


@pytest.fixture
def unauthorized_user_mock():
    """Mock the user authorization check to return False.

    This fixture patches the is_user_authorized function to always return False.
    """
    with patch(
        "bot.handlers.download.is_user_authorized",
        AsyncMock(return_value=False),
    ):
        yield


@pytest.fixture
def isolated_url_storage():
    """Provide an isolated URL storage for testing with complete module isolation.

    This fixture provides stronger isolation than reset_storage by replacing
    the entire URL_STORAGE dictionary at the module level, ensuring complete
    test isolation.

    Importance:
    - Use when reset_storage isn't sufficient
    - Prevents any possibility of test interference
    - Guarantees a clean URL storage environment
    - Useful for tests that manipulate the storage in unusual ways

    Implementation details:
    - Modifies the actual module-level URL_STORAGE variable
    - Returns the storage dict for direct manipulation
    - Restores the original state after the test
    - Less efficient than reset_storage but more thorough

    Usage:
    ```python
    def test_something(isolated_url_storage):
        # storage is completely clean
        assert len(isolated_url_storage) == 0
        
        # can directly manipulate the storage
        isolated_url_storage["test_id"] = ("test_url", None)
        
        # normal API still works
        assert get_url("test_id") == "test_url"
    ```

    Differences from reset_storage:
    - Must be explicitly requested (not autouse)
    - Returns the storage dict for direct manipulation
    - Replaces the entire storage object, not just its contents
    - Does not preserve any URLs from before the test
    """
    # Save original module and its attributes
    import bot.services.storage as storage_module
    from bot.services.storage import URL_STORAGE

    original_storage = URL_STORAGE.copy()

    # Replace storage with empty dict
    storage_module.URL_STORAGE = {}

    yield storage_module.URL_STORAGE

    # Restore original storage
    storage_module.URL_STORAGE = original_storage


@pytest.fixture
def temp_directory():
    """Create a temporary directory for file operations.

    This fixture creates and cleans up a temporary directory for tests
    that need to write files.
    """
    import shutil
    import tempfile

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="vgb_test_")

    yield temp_dir

    # Clean up after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def reset_modules():
    """Reset imported modules to their initial state for thorough isolation.

    This fixture helps manage module-level state by removing specified modules
    from sys.modules, forcing a fresh import on next use.
    
    Importance:
    - Essential for tests that modify module-level variables
    - Prevents side effects from cached or modified modules
    - Allows tests to work with "fresh" modules regardless of import order
    - Critical for modules with global state (like formats, config, storage)
    
    Implementation details:
    - Returns a function that can reset multiple modules at once
    - Removes modules from sys.modules to force fresh imports
    - Doesn't clean up automatically - resets only what you specify
    - Works with any module, not just project modules
    
    Usage:
    ```python
    def test_with_modified_module(reset_modules):
        # Modify a module's globals
        import bot.config
        bot.config.VIDEO_FORMATS = {}
        
        # Reset the module when done
        reset_modules("bot.config")
        
        # Next import will be fresh with original values
        import bot.config  # Fresh import with original VIDEO_FORMATS
    ```
    
    When to use:
    - When you need to modify module-level variables
    - When caching is causing test interference
    - When you need a completely fresh module state
    - As an alternative to monkeypatching when you want a full module reset
    
    Typical modules to reset:
    - bot.config (for configuration changes)
    - bot.services.formats (for format changes)
    - bot.services.storage (for storage changes)
    """
    import sys

    def _reset_module(module_name: str):
        """Remove a module from sys.modules to force a fresh import."""
        if module_name in sys.modules:
            del sys.modules[module_name]

    def reset(*module_names: str):
        """Reset one or more modules by name."""
        for module_name in module_names:
            _reset_module(module_name)

    yield reset

    # Don't cleanup afterwards - each test should explicitly request
    # which modules to reset based on what they're testing
