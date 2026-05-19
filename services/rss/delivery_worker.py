import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from telegram.ext import Application

from config.settings import get_settings
from database.session import AsyncSessionLocal
from models.delivery import Delivery
from models.destination import Destination
from models.enums import DeliveryStatus
from models.post import Post
from services.rss.formatter import (
    TelegramFormatter,
)
from services.rss.publisher import (
    TelegramPublisher,
)


logger = logging.getLogger(__name__)

settings = get_settings()


class DeliveryWorker:
    def __init__(
        self,
        application: Application,
    ) -> None:
        self.application = application

    async def process_pending(
        self,
    ) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Delivery)
                .where(
                    Delivery.status.in_(
                        [
                            DeliveryStatus.PENDING,
                            DeliveryStatus.RETRY,
                        ]
                    )
                )
                .order_by(
                    Delivery.created_at.asc()
                )
                .limit(50)
            )

            deliveries = (
                result.scalars().all()
            )

        if not deliveries:
            logger.info(
                "No pending deliveries"
            )

            return

        logger.info(
            f"Processing "
            f"{len(deliveries)} deliveries"
        )

        for delivery in deliveries:
            try:
                await self._process_delivery(
                    delivery.id
                )
            except Exception as exc:
                logger.exception(
                    f"Delivery worker error: "
                    f"{exc}"
                )

    async def _process_delivery(
        self,
        delivery_id: int,
    ) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    Delivery,
                    Post,
                    Destination,
                )
                .join(
                    Post,
                    Delivery.post_id
                    == Post.id,
                )
                .join(
                    Destination,
                    Delivery.destination_id
                    == Destination.id,
                )
                .where(
                    Delivery.id
                    == delivery_id
                )
            )

            row = result.first()

            if not row:
                return

            delivery, post, destination = row

            if (
                delivery.status
                == DeliveryStatus.DELIVERED
            ):
                return

            delivery.status = (
                DeliveryStatus.PROCESSING
            )

            await session.commit()

            try:
                text = (
                    TelegramFormatter
                    .build_post(
                        title=(
                            post.translated_title
                            or post.title
                        ),
                        content=(
                            post.translated_content
                            or post.content
                            or ""
                        ),
                        source_url=(
                            post.source_url
                        ),
                    )
                )

                message = (
                    await TelegramPublisher.publish(
                        bot=(
                            self.application.bot
                        ),
                        chat_id=(
                            destination
                            .telegram_chat_id
                        ),
                        thread_id=(
                            destination
                            .telegram_thread_id
                        ),
                        text=text,
                        photo=(
                            post.image_url
                        ),
                    )
                )

                delivery.status = (
                    DeliveryStatus.DELIVERED
                )

                delivery.telegram_message_id = (
                    message.message_id
                )

                delivery.delivered_at = (
                    datetime.utcnow()
                )

                await session.commit()

                logger.info(
                    f"Delivery completed: "
                    f"{delivery.id}"
                )

            except Exception as exc:
                logger.exception(
                    f"Delivery failed: "
                    f"{exc}"
                )

                delivery.retry_count += 1

                delivery.last_error = str(exc)

                if (
                    delivery.retry_count
                    >= settings.MAX_RETRY_ATTEMPTS
                ):
                    delivery.status = (
                        DeliveryStatus.FAILED
                    )
                else:
                    delivery.status = (
                        DeliveryStatus.RETRY
                    )

                    delay_minutes = min(
                        delivery.retry_count * 5,
                        60,
                    )

                    delivery.next_retry_at = (
                        datetime.utcnow()
                        + timedelta(
                            minutes=delay_minutes
                        )
                    )

                await session.commit()
