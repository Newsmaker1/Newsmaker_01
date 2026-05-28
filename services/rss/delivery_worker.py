import logging
from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy import (
    select,
)
from telegram.ext import (
    Application,
)

from config.settings import (
    get_settings,
)

from database.session import (
    AsyncSessionLocal,
)

from models.delivery import (
    Delivery,
)

from models.destination import (
    Destination,
)

from models.enums import (
    DeliveryStatus,
)

from models.post import (
    Post,
)

from models.attachment import (
    Attachment,
)

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

    # ==================================================
    # PROCESS PENDING
    # ==================================================

    async def process_pending(
        self,
    ) -> None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(Delivery)
                .where(
                    (
                        Delivery.status
                        == DeliveryStatus.PENDING
                    )
                    |
                    (
                        (
                            Delivery.status
                            == DeliveryStatus.RETRY
                        )
                        &
                        (
                            Delivery.next_retry_at
                            <= datetime.utcnow()
                        )
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

        # ==============================================
        # EMPTY QUEUE
        # ==============================================

        if not deliveries:

            logger.info(
                "No pending deliveries"
            )

            return

        logger.info(
            f"Processing "
            f"{len(deliveries)} deliveries"
        )

        # ==============================================
        # PROCESS DELIVERIES
        # ==============================================

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

    # ==================================================
    # PROCESS DELIVERY
    # ==================================================

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

            # ==========================================
            # LOAD ATTACHMENTS
            # ==========================================
            
            attachments_result = (
                await session.execute(
                    select(Attachment).where(
                        Attachment.post_id
                        == post.id
                    )
                )
            )
            
            attachment_rows = (
                attachments_result
                .scalars()
                .all()
            )
            
            attachments = []
            
            for item in attachment_rows:
            
                attachments.append({
            
                    "file_name": item.file_name,
            
                    "file_url": item.file_url,
            
                    "file_type": item.file_type,
            
                })
            
            # ==========================================
            # ALREADY DELIVERED
            # ==========================================

            if (
                delivery.status
                == DeliveryStatus.DELIVERED
            ):
                return

            # ==========================================
            # DESTINATION CHECK
            # ==========================================

            if destination.is_deleted:

                logger.warning(
                    f"Destination deleted: "
                    f"{destination.id}"
                )

                delivery.status = (
                    DeliveryStatus.FAILED
                )

                delivery.last_error = (
                    "Destination deleted"
                )

                await session.commit()

                return

            if not destination.is_active:

                logger.warning(
                    f"Destination inactive: "
                    f"{destination.id}"
                )

                delivery.status = (
                    DeliveryStatus.FAILED
                )

                delivery.last_error = (
                    "Destination inactive"
                )

                await session.commit()

                return

            # ==========================================
            # PROCESSING STATUS
            # ==========================================

            delivery.status = (
                DeliveryStatus.PROCESSING
            )

            await session.commit()

            try:

                # ======================================
                # BUILD POST
                # ======================================

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
                        attachments=attachments,
                    )
                )

                # ======================================
                # EMPTY TEXT PROTECTION
                # ======================================

                if not text.strip():

                    logger.warning(
                        f"Empty text for post "
                        f"{post.id}"
                    )

                    delivery.status = (
                        DeliveryStatus.FAILED
                    )

                    delivery.last_error = (
                        "Empty formatted text"
                    )

                    await session.commit()

                    return

                # ======================================
                # TELEGRAM PUBLISH
                # ======================================

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

                # ======================================
                # DELIVERY SUCCESS
                # ======================================

                delivery.status = (
                    DeliveryStatus.DELIVERED
                )

                delivery.telegram_message_id = (
                    message.message_id
                )

                delivery.delivered_at = (
                    datetime.utcnow()
                )

                delivery.last_error = None

                await session.commit()

                logger.info(
                    f"Delivery completed: "
                    f"{delivery.id}"
                )

            # ==========================================
            # DELIVERY FAILED
            # ==========================================

            except Exception as exc:

                logger.exception(
                    f"Delivery failed: "
                    f"{exc}"
                )

                delivery.retry_count += 1

                delivery.last_error = str(exc)

                # ======================================
                # MAX RETRIES
                # ======================================

                if (
                    delivery.retry_count
                    >= settings.MAX_RETRY_ATTEMPTS
                ):

                    delivery.status = (
                        DeliveryStatus.FAILED
                    )

                # ======================================
                # RETRY MODE
                # ======================================

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
