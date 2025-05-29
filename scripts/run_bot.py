"""Script to run the bot in test mode."""

import asyncio
import os
import sys

# Add project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger

from bot.main import main

if __name__ == "__main__":
    logger.info("Starting bot in test mode...")
    asyncio.run(main())
