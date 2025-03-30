"""Main module for VideoGrabberBot."""

import asyncio

from aiogram import types
from loguru import logger

from bot.handlers.commands import router as commands_router
from bot.telegram_api.client import bot, dp
from bot.utils.db import init_db

from bot.handlers.download import download_router


# bot/main.py (модифицировать функцию startup)

async def startup() -> None:
    """Perform startup tasks."""
    # Initialize database
    await init_db()

    # Set bot commands for menu display
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="help", description="Show help information"),
            types.BotCommand(command="invite", description="Generate invite link"),
            types.BotCommand(command="cancel", description="Cancel active downloads"),
        ]
    )

    logger.info("Bot has been started successfully")    """Perform startup tasks."""
    # Initialize database
    await init_db()

    # Set bot commands for menu display
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="help", description="Show help information"),
            types.BotCommand(command="invite", description="Generate invite link"),
        ]
    )

    logger.info("Bot has been started successfully")


async def main() -> None:
    """Start the bot."""
    # Register routers
    dp.include_router(commands_router)
    dp.include_router(download_router)

    # Make sure database is initialized
    await startup()

    # Start polling
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
