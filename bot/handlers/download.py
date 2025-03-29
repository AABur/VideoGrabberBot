"""Download handler for processing video links."""

from aiogram import F, Router
from aiogram.types import Message
from loguru import logger

from bot.services.downloader import (
    DownloadError,
    download_youtube_video,
    is_youtube_url,
)
from bot.telegram_api.client import get_bot
from bot.utils.db import is_user_authorized

# Create router for download handlers
download_router = Router()


@download_router.message(F.text.startswith(("http://", "https://")))
async def process_url(message: Message) -> None:
    """
    Process URL message and start download if it's a supported URL.

    Args:
        message: The message containing the URL
    """
    user_id = message.from_user.id
    url = message.text.strip()

    # Check if user is authorized
    if not await is_user_authorized(user_id):
        await message.answer(
            "⛔ <b>Access Denied</b>\n\n"
            "You don't have permission to use this bot.\n"
            "Please contact the administrator for access."
        )
        return

    logger.info(f"Received URL from user {user_id}: {url}")

    # Check if URL is from YouTube
    if is_youtube_url(url):
        try:
            await message.answer(
                "🔍 <b>URL Recognized</b>\n\nStarting download of YouTube video..."
            )

            bot = get_bot()
            await download_youtube_video(bot, message.chat.id, url)

        except DownloadError as e:
            logger.error(f"Download failed: {str(e)}")

    else:
        await message.answer(
            "⚠️ <b>Unsupported URL</b>\n\nCurrently only YouTube links are supported."
        )
