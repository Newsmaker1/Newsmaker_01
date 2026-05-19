import asyncio
import logging

from bot.app import create_application
from scheduler.scheduler import setup_scheduler
from utils.logger import setup_logger


setup_logger()

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting Telegram News SaaS Bot")

    setup_scheduler()

    application = create_application()

    logger.info("Bot polling started")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
