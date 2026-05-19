import asyncio
import logging

from sqlalchemy import select

from database.session import AsyncSessionLocal

from models.source_pack import (
    PackSource,
)

from services.rss.processor import (
    RSSProcessor,
)


logger = logging.getLogger(__name__)


class FeedWorker:
    def __init__(self) -> None:
        self.processor = RSSProcessor()

    # ==================================================
    # SCHEDULER ENTRYPOINT
    # ==================================================

    def run(
        self,
    ) -> None:
        logger.info(
            "Feed worker sync run started"
        )

        loop = asyncio.get_event_loop()

        loop.create_task(
            self.process_sources()
        )

    # ==================================================
    # PROCESS SOURCES
    # ==================================================

    async def process_sources(
        self,
    ) -> None:
        logger.info(
            "Feed worker started"
        )

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PackSource).where(
                    PackSource.is_active.is_(
                        True
                    )
                )
            )

            sources = (
                result.scalars().all()
            )

        if not sources:
            logger.info(
                "No active RSS sources"
            )

            return

        logger.info(
            f"Processing "
            f"{len(sources)} RSS sources"
        )

        for source in sources:
            try:
                logger.info(
                    f"Processing source: "
                    f"{source.id}"
                )

                await (
                    self.processor
                    .process_pack_source(
                        source
                    )
                )

                logger.info(
                    f"Source processed: "
                    f"{source.id}"
                )

            except Exception as exc:
                logger.exception(
                    f"Feed worker error: "
                    f"{exc}"
                )

        logger.info(
            "Feed worker finished"
        )
