import logging
from urllib.parse import (
    urlparse,
)

from sqlalchemy import select

from database.session import AsyncSessionLocal

from models.delivery import Delivery
from models.enums import DeliveryStatus
from models.post import Post
from models.routing_rule import RoutingRule
from models.source_pack import PackSource
from models.source_type import SourceType

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

    def __init__(
        self,
    ) -> None:

        self.fetcher = RSSFetcher()

        self.parser = RSSParser()

        self.translator = RSSTranslator()

    # ==================================================
    # PROCESS SOURCE
    # ==================================================

    async def process_pack_source(
        self,
        source: PackSource,
    ) -> None:

        logger.info(
            f"Processing source: "
            f"{source.source_url}"
        )

        # ==============================================
        # SOURCE TYPE
        # ==============================================

        if (
            source.source_type
            != SourceType.RSS
        ):

            logger.warning(
                f"Unsupported source type: "
                f"{source.source_type}"
            )

            return

        # ==============================================
        # FETCH
        # ==============================================

        result = await self.fetcher.fetch(
            source.source_url
        )

        if (
            result["status"]
            != "success"
        ):

            logger.warning(
                f"Fetch failed: "
                f"{source.source_url}"
            )

            return

        feed = result["feed"]

        if not feed:

            logger.warning(
                f"Empty feed: "
                f"{source.source_url}"
            )

            return

        # ==============================================
        # PROCESS ENTRIES
        # ==============================================

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

    # ==================================================
    # PROCESS ENTRY
    # ==================================================

    async def process_entry(
        self,
        source: PackSource,
        entry,
    ) -> None:

        parsed = self.parser.parse_entry(
            entry
        )

        # ==============================================
        # CLEAN
        # ==============================================

        title = RSSCleaner.clean_html(
            parsed["title"]
        )

        content = RSSCleaner.clean_html(
            parsed["summary"]
        )

        # ==============================================
        # NORMALIZE
        # ==============================================

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

        # ==============================================
        # EMPTY CONTENT
        # ==============================================

        if not title and not content:

            logger.warning(
                "Empty entry skipped"
            )

            return

        # ==============================================
        # HASHES
        # ==============================================

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

        # ==============================================
        # DUPLICATE URL
        # ==============================================

        if await (
            DuplicateDetector
            .is_duplicate_url(
                url_hash
            )
        ):

            logger.info(
                "Duplicate URL skipped"
            )

            return

        # ==============================================
        # DUPLICATE CONTENT
        # ==============================================

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

        # ==============================================
        # TRANSLATION
        # ==============================================

        translated_title = title

        translated_content = content

        if source.translation_enabled:

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

        # ==============================================
        # SIMILAR CONTENT
        # ==============================================

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

        # ==============================================
        # SOURCE DOMAIN
        # ==============================================

        source_domain = None

        if parsed["link"]:

            try:

                source_domain = (
                    urlparse(
                        parsed["link"]
                    ).netloc
                )

            except Exception:

                source_domain = None

        # ==============================================
        # SAVE POST
        # ==============================================

        async with AsyncSessionLocal() as session:

            post = Post(
                pack_id=source.pack_id,
                source_url=parsed["link"],
                source_domain=source_domain,
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

            # ==========================================
            # CREATE DELIVERIES
            # ==========================================

            await self._create_deliveries(
                session=session,
                post=post,
            )

            await session.commit()

            logger.info(
                f"Post created: "
                f"{post.id}"
            )

    # ==================================================
    # CREATE DELIVERIES
    # ==================================================

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

        routing_rules = (
            result.scalars().all()
        )

        # ==============================================
        # CREATE DELIVERY TASKS
        # ==============================================

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
