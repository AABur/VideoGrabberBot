"""Logging configuration module for VideoGrabberBot."""

import sys
from pathlib import Path
from typing import Any, Optional, Union

from aiogram import Bot
from loguru import logger

from bot.config import ADMIN_USER_ID, DATA_DIR


def setup_logger(log_file: Optional[Union[str, Path]] = None) -> None:
    """
    Configure Loguru logger.

    Args:
        log_file: Path to the log file. If None, logs will be saved to DATA_DIR/bot.log
    """
    # Remove default handler
    logger.remove()

    # Set default log file if not provided
    if log_file is None:
        log_file = DATA_DIR / "bot.log"

    # Configure logger format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Add console handler (INFO level and above)
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True,
    )

    # Add file handler (DEBUG level and above)
    logger.add(
        log_file,
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        compression="zip",
        retention="1 month",
    )

    logger.info(f"Logger initialized. Log file: {log_file}")


async def notify_admin(
    bot: Bot, message: str, level: str = "ERROR", **kwargs: Any
) -> None:
    """
    Send notification message to admin.

    Args:
        bot: Initialized Bot instance
        message: Message text to send
        level: Log level (e.g., 'ERROR', 'INFO')
        **kwargs: Additional data to include in the log
    """
    try:
        if level == "ERROR":
            logger.error(f"Admin notification: {message}", **kwargs)
        else:
            logger.log(level, f"Admin notification: {message}", **kwargs)

        # Format message for Telegram
        formatted_message = f"⚠️ {level} ⚠️\n\n{message}"

        # Add additional data if provided
        if kwargs:
            formatted_message += "\n\nAdditional data:\n"
            for key, value in kwargs.items():
                formatted_message += f"- {key}: {value}\n"

        # Send message to admin
        await bot.send_message(ADMIN_USER_ID, formatted_message)
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
