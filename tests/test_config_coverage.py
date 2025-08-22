"""Additional tests for config module to improve coverage."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.config import Config, ConfigurationError


class TestConfigErrorHandling:
    """Test Config class error handling to improve coverage."""

    def test_get_required_str_empty_value(self):
        """Test ConfigurationError for empty required string."""
        config = Config()
        
        with patch.dict(os.environ, {"TEST_KEY": ""}):
            with pytest.raises(ConfigurationError, match="TEST_KEY is not set"):
                config._get_required_str("TEST_KEY")

    def test_get_required_str_missing_value(self):
        """Test ConfigurationError for missing required string."""
        config = Config()
        
        # Ensure key doesn't exist
        if "MISSING_TEST_KEY" in os.environ:
            del os.environ["MISSING_TEST_KEY"]
            
        with pytest.raises(ConfigurationError, match="MISSING_TEST_KEY is not set"):
            config._get_required_str("MISSING_TEST_KEY")

    def test_get_required_int_invalid_value(self):
        """Test ConfigurationError for invalid integer value."""
        config = Config()
        
        with patch.dict(os.environ, {"TEST_INT": "not_a_number"}):
            with pytest.raises(ConfigurationError, match="must be a positive integer"):
                config._get_required_int("TEST_INT")

    def test_get_required_int_zero_value(self):
        """Test ConfigurationError for zero integer value."""
        config = Config()
        
        with patch.dict(os.environ, {"TEST_INT": "0"}):
            with pytest.raises(ConfigurationError, match="must be a positive integer"):
                config._get_required_int("TEST_INT")

    def test_get_required_int_negative_value(self):
        """Test ConfigurationError for negative integer value."""
        config = Config()
        
        with patch.dict(os.environ, {"TEST_INT": "-5"}):
            with pytest.raises(ConfigurationError, match="must be a positive integer"):
                config._get_required_int("TEST_INT")

    def test_setup_directories_permission_error(self, tmp_path):
        """Test ConfigurationError when directories cannot be created."""
        config = Config()
        
        # Create a read-only parent directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        # Try to create subdirectories
        config.DATA_DIR = readonly_dir / "data"
        config.TEMP_DIR = readonly_dir / "temp"
        
        try:
            with pytest.raises(ConfigurationError, match="Failed to create directories"):
                config._setup_directories()
        finally:
            # Cleanup: restore write permissions
            readonly_dir.chmod(0o755)


class TestConfigValidation:
    """Test Config.validate_all() method to improve coverage."""

    def test_validate_all_success(self):
        """Test successful validation."""
        config = Config()
        
        # Mock valid environment
        with patch.dict(os.environ, {
            "TELEGRAM_TOKEN": "valid_token",
            "ADMIN_USER_ID": "123456",
            "LOG_LEVEL": "INFO",
            "MAX_FILE_SIZE": "50",
            "DOWNLOAD_TIMEOUT": "300"
        }):
            # Create a new config with mocked values
            test_config = Config()
            test_config.LOG_LEVEL = "INFO"
            test_config.MAX_FILE_SIZE = 50
            test_config.DOWNLOAD_TIMEOUT = 300
            test_config.BOT_NAME = "TestBot"
            
            # Should not raise any exception
            test_config.validate_all()

    def test_validate_all_invalid_log_level(self):
        """Test validation failure for invalid log level."""
        config = Config()
        config.LOG_LEVEL = "INVALID_LEVEL"
        config.MAX_FILE_SIZE = 50
        config.DOWNLOAD_TIMEOUT = 300
        
        with pytest.raises(ConfigurationError, match="Invalid LOG_LEVEL"):
            config.validate_all()

    def test_validate_all_invalid_max_file_size(self):
        """Test validation failure for invalid max file size."""
        config = Config()
        config.LOG_LEVEL = "INFO"
        config.MAX_FILE_SIZE = -1
        config.DOWNLOAD_TIMEOUT = 300
        
        with pytest.raises(ConfigurationError, match="MAX_FILE_SIZE must be positive"):
            config.validate_all()

    def test_validate_all_zero_max_file_size(self):
        """Test validation failure for zero max file size."""
        config = Config()
        config.LOG_LEVEL = "INFO"
        config.MAX_FILE_SIZE = 0
        config.DOWNLOAD_TIMEOUT = 300
        
        with pytest.raises(ConfigurationError, match="MAX_FILE_SIZE must be positive"):
            config.validate_all()

    def test_validate_all_invalid_download_timeout(self):
        """Test validation failure for invalid download timeout."""
        config = Config()
        config.LOG_LEVEL = "INFO"
        config.MAX_FILE_SIZE = 50
        config.DOWNLOAD_TIMEOUT = -1
        
        with pytest.raises(ConfigurationError, match="DOWNLOAD_TIMEOUT must be positive"):
            config.validate_all()

    def test_validate_all_zero_download_timeout(self):
        """Test validation failure for zero download timeout."""
        config = Config()
        config.LOG_LEVEL = "INFO"
        config.MAX_FILE_SIZE = 50
        config.DOWNLOAD_TIMEOUT = 0
        
        with pytest.raises(ConfigurationError, match="DOWNLOAD_TIMEOUT must be positive"):
            config.validate_all()

    def test_validate_all_valid_log_levels(self):
        """Test validation succeeds for all valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = Config()
            config.LOG_LEVEL = level
            config.MAX_FILE_SIZE = 50
            config.DOWNLOAD_TIMEOUT = 300
            config.BOT_NAME = "TestBot"
            
            # Should not raise any exception
            config.validate_all()