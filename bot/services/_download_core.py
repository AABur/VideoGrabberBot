# bot/services/_download_core.py
"""Core download engine using yt-dlp."""

from pathlib import Path
from typing import Any, Dict

import yt_dlp
from loguru import logger

from bot.utils.exceptions import (
    DownloadError,
    NetworkError,
    UnsupportedFormatError,
    VideoNotFoundError,
    VideoTooLargeError,
)

# Constants
MB_SIZE = 1024 * 1024  # 1 MB in bytes
TELEGRAM_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50MB actual limit for Bot API


def _create_ydl_options(format_string: str, temp_download_path: Path) -> Dict[str, Any]:
    """Create yt-dlp options dictionary with minimal optimizations."""
    return {
        "format": format_string,
        "outtmpl": str(temp_download_path / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        # Only essential optimizations to avoid signature extraction issues
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
            ),
        },
        # Shorter timeouts to prevent hanging
        "socket_timeout": 30,
        "retries": 2,
    }


def _sync_download_video_file(
    url: str, ydl_opts: Dict[str, Any], temp_download_path: Path
) -> tuple[Path, Dict[str, Any]]:
    """Synchronous download function to be run in thread pool."""
    # Late import to keep config mocking working in tests (avoids circular import at module level)
    from bot.services.downloader import _validate_file_size  # noqa: PLC0415

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Extracting info: {url}")

            try:
                video_info = ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e).lower()
                if "not available" in error_msg or "video not found" in error_msg:
                    raise VideoNotFoundError(
                        "Video not found or unavailable", context={"url": url, "original_error": str(e)}
                    ) from e
                if "unsupported url" in error_msg or "unsupported format" in error_msg:
                    raise UnsupportedFormatError(
                        "Video format not supported", context={"url": url, "original_error": str(e)}
                    ) from e
                raise NetworkError(
                    "Network error during video info extraction", context={"url": url, "original_error": str(e)}
                ) from e

            # Check expected file size if available
            if video_info and video_info.get("filesize"):
                expected_size = video_info["filesize"]
                _validate_file_size(expected_size, url)

            logger.debug(f"Starting download with options: {ydl_opts}")

            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                raise NetworkError(
                    "Network error during video download", context={"url": url, "original_error": str(e)}
                ) from e

            # Get downloaded file path
            downloaded_files = list(temp_download_path.glob("*"))
            if not downloaded_files:
                raise DownloadError(
                    "Download completed but no files found", context={"url": url, "temp_path": str(temp_download_path)}
                )

            file_path = downloaded_files[0]
            file_size = file_path.stat().st_size

            # Check actual file size
            _validate_file_size(file_size, url, file_path)

            logger.info(f"Download completed: {file_path} ({file_size} bytes)")
            return file_path, video_info

    except Exception as e:
        if isinstance(e, (VideoNotFoundError, UnsupportedFormatError, NetworkError, VideoTooLargeError)):
            raise
        raise DownloadError("Unexpected error during download", context={"url": url, "original_error": str(e)}) from e
