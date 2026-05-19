import logging

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)

from config.settings import get_settings
from services.rss.delivery_worker import (
    DeliveryWorker,
)
from services.rss.feed_worker import (
    FeedWorker,
)


logger = logging.getLogger(__name__)

settings = get_settings()

scheduler = AsyncIOScheduler()


def setup_scheduler(
    application,
) -> None:
    feed_worker = FeedWorker()

    delivery_worker = DeliveryWorker(
        application=application
    )

    scheduler.add_job(
        feed_worker.process_sources,
        trigger="interval",
        minutes=(
            settings
            .FETCH_INTERVAL_MINUTES
        ),
        id="rss_feed_worker",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.add_job(
        delivery_worker.process_pending,
        trigger="interval",
        seconds=15,
        id="delivery_worker",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()

    logger.info(
        "Scheduler started"
    )
