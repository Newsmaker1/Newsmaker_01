import logging

from sqlalchemy import (
    select,
)

from database.session import (
    AsyncSessionLocal,
)

from models.destination import (
    Destination,
)

from models.feed_item import (
    FeedItem,
)

from models.pack_destination import (
    PackDestination,
)

from models.rss_source import (
    RSSSource,
)

from services.telegram.sender import (
    send_message,
)

logger = logging.getLogger(__name__)


async def process_feed_item(
    feed_item_id: int,
):

    async with AsyncSessionLocal() as session:

        # ==========================================
        # FEED ITEM
        # ==========================================

        feed_item = await session.get(
            FeedItem,
            feed_item_id,
        )

        if not feed_item:

            logger.warning(
                f"FeedItem not found: "
                f"{feed_item_id}"
            )

            return

        # ==========================================
        # RSS SOURCE
        # ==========================================

        rss_source = await session.get(
            RSSSource,
            feed_item.source_id,
        )

        if not rss_source:

            logger.warning(
                f"RSS Source not found: "
                f"{feed_item.source_id}"
            )

            return

        if not rss_source.pack_id:

            logger.info(
                f"RSS source without pack: "
                f"{rss_source.id}"
            )

            return

        # ==========================================
        # ROUTES
        # ==========================================

        result = await session.execute(
            select(PackDestination)
            .where(
                PackDestination.pack_id
                == rss_source.pack_id,
                PackDestination.is_active
                == True,
            )
        )

        routes = result.scalars().all()

        if not routes:

            logger.info(
                f"No routes for pack "
                f"{rss_source.pack_id}"
            )

            return

        # ==========================================
        # MESSAGE
        # ==========================================

        message_text = build_message(
            feed_item
        )

        # ==========================================
        # DELIVERY
        # ==========================================

        for route in routes:

            destination = (
                route.destination
            )

            if not destination:
                continue

            if destination.is_deleted:
                continue

            if not destination.is_active:
                continue

            success = await send_message(
                chat_id=(
                    destination.telegram_chat_id
                ),
                text=message_text,
                thread_id=(
                    destination.telegram_thread_id
                ),
            )

            if success:

                logger.info(
                    f"Delivered "
                    f"FeedItem "
                    f"{feed_item.id} "
                    f"to "
                    f"{destination.id}"
                )

            else:

                logger.warning(
                    f"Delivery failed "
                    f"FeedItem "
                    f"{feed_item.id} "
                    f"to "
                    f"{destination.id}"
                )


def build_message(
    feed_item: FeedItem,
):

    text = ""

    # ==========================================
    # TITLE
    # ==========================================

    if feed_item.title:

        text += (
            f"📰 {feed_item.title}\n\n"
        )

    # ==========================================
    # SUMMARY
    # ==========================================

    if feed_item.summary:

        text += (
            f"{feed_item.summary}\n\n"
        )

    # ==========================================
    # URL
    # ==========================================

    if feed_item.url:

        text += (
            f"{feed_item.url}"
        )

    return text[:4096]
