"""Script to run the bot in test mode."""

import asyncio
import sys
import os

# Add project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.main import main
from loguru import logger

if __name__ == "__main__":
    logger.info("Starting bot in test mode...")
    asyncio.run(main())
