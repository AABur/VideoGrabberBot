"""Additional tests for downloader module to improve coverage."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yt_dlp

from bot.services.downloader import (
    NetworkError,
    UnsupportedFormatError,
    VideoNotFoundError,
    VideoTooLargeError,
    _validate_file_size,
    _sync_download_video_file,
    _cleanup_temp_directory,
)


class TestFileSizeCheck:
    """Test file size checking functionality."""

    def test_validate_file_size_oversized_with_file(self, tmp_path):
        """Test file size check when file is too large and exists."""
        # Create a test file
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"test content")
        
        # Mock config with small max file size
        with patch("bot.services.downloader.config") as mock_config:
            mock_config.MAX_FILE_SIZE = 10  # Very small limit
            
            with pytest.raises(VideoTooLargeError, match="File size .* exceeds limit"):
                _validate_file_size(1024 * 1024, "http://test.url", test_file)  # 1MB file
                
            # File should be deleted
            assert not test_file.exists()

    def test_validate_file_size_oversized_no_file(self):
        """Test file size check when file is too large but no file exists."""
        with patch("bot.services.downloader.config") as mock_config:
            mock_config.MAX_FILE_SIZE = 10  # Very small limit
            
            with pytest.raises(VideoTooLargeError, match="File size .* exceeds limit"):
                _validate_file_size(1024 * 1024, "http://test.url", None)

    def test_validate_file_size_within_limit(self, tmp_path):
        """Test file size check when file is within limit."""
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"test content")
        
        with patch("bot.services.downloader.config") as mock_config:
            mock_config.MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB limit
            
            # Should not raise exception
            _validate_file_size(1024, "http://test.url", test_file)
            
            # File should still exist
            assert test_file.exists()


class TestSyncDownloadVideoFile:
    """Test sync download video file function."""

    def test_extract_info_video_not_found_error(self, tmp_path):
        """Test extract info with video not found error."""
        url = "http://test.url"
        ydl_opts = {"format": "best"}
        temp_path = tmp_path
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Video not found or not available")
        
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl
            
            with pytest.raises(VideoNotFoundError, match="Video not found or unavailable"):
                _sync_download_video_file(url, ydl_opts, temp_path)

    def test_extract_info_unsupported_format_error(self, tmp_path):
        """Test extract info with unsupported format error."""
        url = "http://test.url"
        ydl_opts = {"format": "best"}
        temp_path = tmp_path
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Unsupported URL or format")
        
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl
            
            with pytest.raises(UnsupportedFormatError, match="Video format not supported"):
                _sync_download_video_file(url, ydl_opts, temp_path)

    def test_extract_info_network_error(self, tmp_path):
        """Test extract info with network error."""
        url = "http://test.url"
        ydl_opts = {"format": "best"}
        temp_path = tmp_path
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Connection failed")
        
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl
            
            with pytest.raises(NetworkError, match="Network error during video info extraction"):
                _sync_download_video_file(url, ydl_opts, temp_path)

    def test_expected_file_size_check(self, tmp_path):
        """Test expected file size validation."""
        url = "http://test.url"
        ydl_opts = {"format": "best"}
        temp_path = tmp_path
        
        # Create test file
        test_file = temp_path / "test_video.mp4"
        test_file.write_bytes(b"test content")
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {"filesize": 1024 * 1024 * 100}  # Large file
        mock_ydl.download.return_value = None
        
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class, \
             patch("bot.services.downloader.config") as mock_config, \
             patch("pathlib.Path.glob", return_value=[test_file]):
            
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl
            mock_config.MAX_FILE_SIZE = 10  # Very small limit
            
            with pytest.raises(VideoTooLargeError):
                _sync_download_video_file(url, ydl_opts, temp_path)

    def test_download_network_error(self, tmp_path):
        """Test download with network error."""
        url = "http://test.url"
        ydl_opts = {"format": "best"}
        temp_path = tmp_path
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {"filesize": 1024}
        mock_ydl.download.side_effect = yt_dlp.utils.DownloadError("Network error during download")
        
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class, \
             patch("bot.services.downloader.config") as mock_config:
            
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl
            mock_config.MAX_FILE_SIZE = 1024 * 1024  # 1MB limit
            
            with pytest.raises(NetworkError, match="Network error during video download"):
                _sync_download_video_file(url, ydl_opts, temp_path)


class TestCleanupTempDirectory:
    """Test cleanup temporary directory function."""

    def test_cleanup_temp_directory_success(self, tmp_path):
        """Test successful cleanup of temporary directory."""
        temp_dir = str(tmp_path / "test_temp")
        
        # Create the directory first
        import os
        os.makedirs(temp_dir, exist_ok=True)
        
        # Add a file to make sure directory is not empty
        test_file = Path(temp_dir) / "test_file.txt"
        test_file.write_text("test content")
        
        # Cleanup should not raise exception
        _cleanup_temp_directory(temp_dir)
        
        # Directory should no longer exist
        assert not os.path.exists(temp_dir)

    def test_cleanup_temp_directory_not_exists(self):
        """Test cleanup of non-existent directory."""
        temp_dir = "/non/existent/directory"
        
        # Should not raise exception
        _cleanup_temp_directory(temp_dir)

    def test_cleanup_temp_directory_failure(self, tmp_path):
        """Test cleanup failure handling."""
        temp_dir = str(tmp_path / "test_temp")
        
        # Create the directory
        import os
        os.makedirs(temp_dir, exist_ok=True)
        
        with patch("os.path.exists", return_value=True), \
             patch("shutil.rmtree", side_effect=PermissionError("Permission denied")), \
             patch("bot.services.downloader.logger.error") as mock_logger:
            
            # Should not raise exception but log error
            _cleanup_temp_directory(temp_dir)
            
            # Should have logged the error
            mock_logger.assert_called_once()
            assert "Failed to clean up temporary directory" in mock_logger.call_args[0][0]


