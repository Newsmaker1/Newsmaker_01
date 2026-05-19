import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler


logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    logger.info("Scheduler initialized")
