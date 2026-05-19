import asyncio
import logging

from bot.app import create_application
from scheduler.scheduler import setup_scheduler


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


async def main():
    logger.info(
        "Starting Telegram News SaaS Bot"
    )

    application = create_application()

    await application.initialize()

    await application.start()

    await application.updater.start_polling()

    logger.info(
        "Bot polling started"
    )

    # START SCHEDULER ONLY AFTER LOOP READY
    setup_scheduler(application)

    logger.info(
        "Scheduler started"
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
