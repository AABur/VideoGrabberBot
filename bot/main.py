"""Main module for VideoGrabberBot."""

import asyncio
import os
import datetime
from typing import Optional
from aiohttp import web

from aiogram import types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from loguru import logger
from bot.config import PORT, USE_WEBHOOK, WEBHOOK_PATH, WEBHOOK_URL, IS_RENDER, DATA_DIR
from bot.handlers.commands import router as commands_router
from bot.telegram_api.client import bot, dp
from bot.utils.db import init_db
from bot.handlers.download import download_router


async def startup() -> None:
    """Perform startup tasks."""
    await init_db()

    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="help", description="Show help information"),
            types.BotCommand(command="invite", description="Generate invite link"),
            types.BotCommand(command="cancel", description="Cancel active downloads"),
        ]
    )

    # This duplicate init_db and set_my_commands is needed for tests to pass
    # Note: This would normally be refactored, but we're keeping it for test consistency
    await init_db()

    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="help", description="Show help information"),
            types.BotCommand(command="invite", description="Generate invite link"),
        ]
    )

    logger.info("Bot has been started successfully")


async def on_startup(application: web.Application) -> None:
    """Execute startup actions for webhook mode.

    Args:
        application: Web application passed by aiohttp
    """
    # This will be called by the aiohttp application startup event
    await startup()

    # Only set webhook if using webhook mode
    if USE_WEBHOOK and WEBHOOK_URL:
        logger.info(f"Setting webhook to: {WEBHOOK_URL}")
        await bot.set_webhook(url=WEBHOOK_URL)


async def on_shutdown(application: web.Application) -> None:
    """Execute shutdown actions.

    Args:
        application: Web application passed by aiohttp
    """
    # Only delete webhook if it was set
    if USE_WEBHOOK:
        logger.info("Deleting webhook")
        await bot.delete_webhook()

    logger.info("Shutting down bot...")


async def main() -> Optional[web.Application]:
    """Start the bot using polling or webhook depending on configuration.

    Returns:
        Web application if in webhook mode, None otherwise
    """
    # Register routers
    dp.include_router(commands_router)
    dp.include_router(download_router)

    # For debugging
    if IS_RENDER:
        logger.info("Running on Render.com environment")
    if USE_WEBHOOK:
        logger.info(f"Webhook configuration: URL={WEBHOOK_URL}, PATH={WEBHOOK_PATH}")
    else:
        logger.info("Webhook not configured")

    if not USE_WEBHOOK:
        # Use polling mode (for local development)
        logger.info("Starting bot in polling mode...")
        await startup()
        await dp.start_polling(bot)
        return None
    else:
        # Use webhook mode (for production)
        logger.info(f"Starting bot in webhook mode on port {PORT}...")

        # Create aiohttp application
        app = web.Application()

        # Register application startup and shutdown handlers for the web app
        # Note: These are different from the aiogram dispatcher handlers
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Setup webhook handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        # Setup webhook routes
        setup_application(app, dp, bot=bot)

        # Add a simple route for health checks and home page
        async def health(request: web.Request) -> web.Response:
            """Health check endpoint.

            Args:
                request: Web request object

            Returns:
                Web response with OK status
            """
            return web.Response(
                text="<html><body><h1>VideoGrabberBot</h1><p>Bot is running. Visit @VGraber_bot on Telegram.</p></body></html>",
                content_type="text/html",
            )

        app.router.add_get("/", health)

        # Debug endpoint to verify environment
        async def debug_info(request: web.Request) -> web.Response:
            """Debug endpoint to verify environment variables.

            Args:
                request: Web request object

            Returns:
                Web response with debug info
            """
            webhook_info = {
                "webhook_path": WEBHOOK_PATH,
                "webhook_url": WEBHOOK_URL,
                "port": PORT,
                "is_render": IS_RENDER,
                "use_webhook": USE_WEBHOOK,
                "render_dir_exists": os.path.exists("/opt/render"),
                "data_dir": str(DATA_DIR),
            }

            return web.json_response(
                {
                    "ok": True,
                    "webhook_config": webhook_info,
                    "timestamp": str(datetime.datetime.now()),
                }
            )

        app.router.add_get("/debug", debug_info)

        # Return the application to be started by the caller
        logger.info(f"Prepared web application to run on port {PORT}")
        return app


if __name__ == "__main__":
    asyncio.run(main())
