import logging

from sqlalchemy import select

from database.session import AsyncSessionLocal
from models.delivery import Delivery
from models.enums import DeliveryStatus
from models.post import Post
from models.routing_rule import RoutingRule
from models.source_pack import PackSource
from services.rss.cleaner import RSSCleaner
from services.rss.duplicate_detector import (
    DuplicateDetector,
)
from services.rss.fetcher import RSSFetcher
from services.rss.normalizer import RSSNormalizer
from services.rss.parser import RSSParser
from services.rss.translator import RSSTranslator


logger = logging.getLogger(__name__)


class RSSProcessor:
    def __init__(self) -> None:
        self.fetcher = RSSFetcher()
        self.parser = RSSParser()
        self.translator = RSSTranslator()

    async def process_pack_source(
        self,
        source: PackSource,
    ) -> None:
        logger.info(
            f"Processing source: "
            f"{source.source_url}"
        )

        result = await self.fetcher.fetch(
            source.source_url
        )

        if result["status"] != "success":
            return

        feed = result["feed"]

        if not feed:
            return

        for entry in feed.entries:
            try:
                await self.process_entry(
                    source=source,
                    entry=entry,
                )
            except Exception as exc:
                logger.exception(
                    f"Entry processing error: "
                    f"{exc}"
                )

    async def process_entry(
        self,
        source: PackSource,
        entry,
    ) -> None:
        parsed = self.parser.parse_entry(
            entry
        )

        title = RSSCleaner.clean_html(
            parsed["title"]
        )

        content = RSSCleaner.clean_html(
            parsed["summary"]
        )

        title = (
            RSSNormalizer.normalize_text(
                title
            )
        )

        content = (
            RSSNormalizer.normalize_text(
                content
            )
        )

        url_hash = (
            DuplicateDetector.make_sha256(
                parsed["link"]
            )
        )

        content_hash = (
            DuplicateDetector.make_sha256(
                content
            )
        )

        if await (
            DuplicateDetector
            .is_duplicate_url(url_hash)
        ):
            logger.info(
                "Duplicate URL skipped"
            )

            return

        if await (
            DuplicateDetector
            .is_duplicate_content(
                content_hash
            )
        ):
            logger.info(
                "Duplicate content skipped"
            )

            return

        translated_title = (
            await self.translator.translate(
                title
            )
        )

        translated_content = (
            await self.translator.translate(
                content
            )
        )

        if await (
            DuplicateDetector
            .is_similar_content(
                translated_content
            )
        ):
            logger.info(
                "Similar content skipped"
            )

            return

        async with AsyncSessionLocal() as session:
            post = Post(
                pack_id=source.pack_id,
                source_url=parsed["link"],
                source_domain=(
                    parsed["link"]
                    .split("/")[2]
                    if "://"
                    in parsed["link"]
                    else None
                ),
                title=title,
                content=content,
                translated_title=(
                    translated_title
                ),
                translated_content=(
                    translated_content
                ),
                image_url=(
                    parsed["image_url"]
                ),
                url_hash=url_hash,
                content_hash=content_hash,
                similarity_hash=(
                    DuplicateDetector
                    .make_sha256(
                        translated_content[:500]
                    )
                ),
                published_at=(
                    parsed["published_at"]
                ),
            )

            session.add(post)

            await session.flush()

            await self._create_deliveries(
                session=session,
                post=post,
            )

            await session.commit()

            logger.info(
                f"Post created: {post.id}"
            )

    async def _create_deliveries(
        self,
        session,
        post: Post,
    ) -> None:
        result = await session.execute(
            select(RoutingRule).where(
                RoutingRule.pack_id
                == post.pack_id,
                RoutingRule.is_active.is_(
                    True
                ),
            )
        )

        routing_rules = result.scalars().all()

        for rule in routing_rules:
            delivery = Delivery(
                post_id=post.id,
                destination_id=(
                    rule.destination_id
                ),
                status=(
                    DeliveryStatus.PENDING
                ),
            )

            session.add(delivery)

        logger.info(
            f"Created "
            f"{len(routing_rules)} "
            f"deliveries"
        )
