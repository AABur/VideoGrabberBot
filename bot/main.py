"""Main module for VideoGrabberBot."""

import asyncio
import sys
from aiohttp import web

from aiogram import types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from loguru import logger

from bot.config import PORT, USE_WEBHOOK, WEBHOOK_PATH, WEBHOOK_URL
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

    logger.info("Bot has been started successfully")


async def on_startup(bot_instance: object) -> None:
    """Execute startup actions for webhook mode.
    
    Args:
        bot_instance: Bot instance object passed by aiogram
    """
    await startup()
    
    # Only set webhook if using webhook mode
    if USE_WEBHOOK and WEBHOOK_URL:
        logger.info(f"Setting webhook to: {WEBHOOK_URL}")
        await bot.set_webhook(url=WEBHOOK_URL)
        

async def on_shutdown(bot_instance: object) -> None:
    """Execute shutdown actions.
    
    Args:
        bot_instance: Bot instance object passed by aiogram
    """
    # Only delete webhook if it was set
    if USE_WEBHOOK:
        logger.info("Deleting webhook")
        await bot.delete_webhook()
    
    logger.info("Shutting down bot...")


async def main() -> None:
    """Start the bot using polling or webhook depending on configuration."""
    # Register routers
    dp.include_router(commands_router)
    dp.include_router(download_router)
    
    if not USE_WEBHOOK:
        # Use polling mode (for local development)
        logger.info("Starting bot in polling mode...")
        await startup()
        await dp.start_polling(bot)
    else:
        # Use webhook mode (for production)
        logger.info(f"Starting bot in webhook mode on port {PORT}...")
        
        # Register startup and shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Create aiohttp application
        app = web.Application()
        
        # Setup webhook handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        
        # Setup webhook routes
        setup_application(app, dp, bot=bot)
        
        # Add a simple route for health checks
        async def health(request: web.Request) -> web.Response:
            """Health check endpoint.
            
            Args:
                request: Web request object
                
            Returns:
                Web response with OK status
            """
            return web.Response(text="OK")
        
        app.router.add_get("/", health)
        
        # Start the application
        try:
            logger.info(f"Starting web server on port {PORT}")
            web.run_app(app, host="0.0.0.0", port=PORT)
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
