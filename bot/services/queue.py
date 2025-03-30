# bot/services/queue.py
"""Queue management for download tasks."""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from loguru import logger


@dataclass
class DownloadTask:
    """Represents a download task in the queue."""

    chat_id: int
    url: str
    format_string: str
    status_message_id: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None


class DownloadQueue:
    """Manages a queue of download tasks."""

    def __init__(self):
        """Initialize download queue."""
        self.queue = asyncio.Queue()
        self.is_processing = False
        self.current_task: Optional[DownloadTask] = None
        self._worker_task = None

    async def add_task(self, task: DownloadTask) -> int:
        """
        Add a task to the queue.

        Args:
            task: Download task to add

        Returns:
            Current queue size after adding the task
        """
        await self.queue.put(task)
        queue_size = self.queue.qsize()
        logger.info(
            f"Task added to queue: {task.url}, format: {task.format_string}, position: {queue_size}"
        )

        # Start worker if not already running
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())

        return queue_size

    async def _process_queue(self):
        """Process tasks in the queue sequentially."""
        while not self.queue.empty():
            self.is_processing = True
            self.current_task = await self.queue.get()

            try:
                logger.info(
                    f"Processing task: {self.current_task.url}, format: {self.current_task.format_string}"
                )

                # Import here to avoid circular imports
                from bot.services.downloader import download_youtube_video

                bot = self.current_task.additional_data.get("bot")
                if not bot:
                    logger.error("Bot instance not provided in task data")
                    continue

                # Download the video
                await download_youtube_video(
                    bot,
                    self.current_task.chat_id,
                    self.current_task.url,
                    self.current_task.format_string,
                )

                logger.info(f"Task completed: {self.current_task.url}")

            except Exception as e:
                logger.error(f"Error processing task: {str(e)}", exc_info=True)
            finally:
                self.queue.task_done()
                self.current_task = None

        self.is_processing = False

    def get_queue_position(self, chat_id: int, url: str) -> Optional[int]:
        """
        Get position of a task in the queue.

        Args:
            chat_id: User chat ID
            url: URL being downloaded

        Returns:
            Position in queue (1-based) or None if not found
        """
        if self.queue.empty():
            return None

        # Create a list from queue items (without removing them)
        queue_items = list(self.queue._queue)

        for i, task in enumerate(queue_items):
            if task.chat_id == chat_id and task.url == url:
                return i + 1

        return None

    def is_user_in_queue(self, chat_id: int) -> bool:
        """
        Check if user has tasks in queue.

        Args:
            chat_id: User chat ID

        Returns:
            True if user has tasks in queue, False otherwise
        """
        if self.queue.empty():
            return False

        # Check if user has a task in the queue
        queue_items = list(self.queue._queue)
        return any(task.chat_id == chat_id for task in queue_items)

    def clear_user_tasks(self, chat_id: int) -> int:
        """
        Remove all tasks for a specific user.

        Args:
            chat_id: User chat ID

        Returns:
            Number of tasks removed
        """
        if self.queue.empty():
            return 0

        # Create a new queue without the specified user's tasks
        new_queue = asyncio.Queue()
        removed_count = 0

        # Move items to the new queue, skipping those from the specified user
        old_queue_items = list(self.queue._queue)
        self.queue = asyncio.Queue()

        for task in old_queue_items:
            if task.chat_id == chat_id:
                removed_count += 1
            else:
                new_queue.put_nowait(task)

        self.queue = new_queue
        logger.info(f"Removed {removed_count} tasks for chat_id: {chat_id}")
        return removed_count


# Global queue instance
download_queue = DownloadQueue()
