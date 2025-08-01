#!/usr/bin/env python
"""
Test runner for VideoGrabberBot.

This script starts a development version of the bot for manual testing.
It sets up a minimal environment and initializes all required components.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Set up basic logging for the test run
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add the project root to path - this is needed for imports to work
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import bot modules after path is set
from bot.main import main  # noqa: E402
from bot.utils.db import init_db  # noqa: E402
from bot.utils.logging import setup_logger  # noqa: E402


async def test_runner() -> None:
    """Run the bot in test mode with minimal setup."""
    # Setup logging first
    setup_logger()

    from loguru import logger

    logger.info("Starting VideoGrabberBot in test mode...")
    logger.info("Press Ctrl+C to stop the bot.")

    # Initialize database
    await init_db()
    # Run the main bot function
    await main()


if __name__ == "__main__":
    try:
        # Run the async loop
        asyncio.run(test_runner())
    except KeyboardInterrupt:
        logging.info("\nBot stopped by user.")
    except Exception as e:
        logging.error(f"Error running bot: {e}")
        sys.exit(1)
