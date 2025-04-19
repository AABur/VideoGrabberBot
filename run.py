#!/usr/bin/env python
"""Run script for VideoGrabberBot."""

import asyncio
import logging
import sys

from aiohttp import web
from loguru import logger


def setup_logging():
    """Configure logger."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.info("Starting VideoGrabberBot...")


async def start_bot():
    """Start the bot."""
    # Import here to avoid circular imports
    from bot.main import main
    from bot.config import PORT, USE_WEBHOOK

    app_or_none = await main()

    # If main() returned a web application, start it
    if app_or_none is not None and USE_WEBHOOK:
        logger.info(f"Starting web server on port {PORT}")
        # Using a runner to properly handle async startup/shutdown
        runner = web.AppRunner(app_or_none)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)

        try:
            await site.start()
            logger.info(f"Server started on port {PORT}")

            # Keep the server running
            while True:
                await asyncio.sleep(
                    3600
                )  # Sleep for an hour, wake up to check if we need to stop
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            logger.info("Shutting down web server")
            await runner.cleanup()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(start_bot())
