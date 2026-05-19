import logging

from sqlalchemy import select

from database.session import AsyncSessionLocal
from models.source_pack import PackSource
from services.rss.processor import (
    RSSProcessor,
)


logger = logging.getLogger(__name__)


class FeedWorker:
    def __init__(self) -> None:
        self.processor = RSSProcessor()

    async def process_sources(
        self,
    ) -> None:
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
                await (
                    self.processor
                    .process_pack_source(
                        source
                    )
                )
            except Exception as exc:
                logger.exception(
                    f"Feed worker error: "
                    f"{exc}"
                )
