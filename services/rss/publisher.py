import asyncio
import logging

from telegram.constants import (
    ParseMode,
)

from telegram.error import (
    BadRequest,
    RetryAfter,
    TimedOut,
)

from config.settings import (
    get_settings,
)


logger = logging.getLogger(__name__)

settings = get_settings()


class TelegramPublisher:

    # ==================================================
    # PUBLISH
    # ==================================================

    @staticmethod
    async def publish(
        bot,
        chat_id: int,
        text: str,
        thread_id: int | None = None,
        photo: str | None = None,
    ):

        try:

            # ==========================================
            # FLOOD DELAY
            # ==========================================

            await asyncio.sleep(
                settings.TELEGRAM_SEND_DELAY
            )

            # ==========================================
            # EMPTY TEXT PROTECTION
            # ==========================================

            if not text.strip():

                raise ValueError(
                    "Empty publish text"
                )

            # ==========================================
            # TELEGRAM LIMIT
            # ==========================================

            if len(text) > 4096:

                text = text[:4000] + "..."

            # ==========================================
            # PHOTO POST
            # ==========================================

            if photo:

                try:

                    message = (
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=text[:1024],
                            parse_mode=(
                                ParseMode.HTML
                            ),
                            message_thread_id=(
                                thread_id
                            ),
                        )
                    )

                # ======================================
                # PHOTO FAILED
                # ======================================

                except Exception as photo_exc:

                    logger.warning(
                        f"Photo publish failed: "
                        f"{photo_exc}"
                    )

                    message = (
                        await bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            parse_mode=(
                                ParseMode.HTML
                            ),
                            disable_web_page_preview=False,
                            message_thread_id=(
                                thread_id
                            ),
                        )
                    )

            # ==========================================
            # TEXT POST
            # ==========================================

            else:

                message = (
                    await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode=(
                            ParseMode.HTML
                        ),
                        disable_web_page_preview=False,
                        message_thread_id=(
                            thread_id
                        ),
                    )
                )

            logger.info(
                f"Message delivered "
                f"to {chat_id}"
            )

            return message

        # ==============================================
        # FLOOD CONTROL
        # ==============================================

        except RetryAfter as exc:

            logger.warning(
                f"Flood control triggered: "
                f"{exc.retry_after}"
            )

            await asyncio.sleep(
                exc.retry_after
            )

            return (
                await TelegramPublisher.publish(
                    bot=bot,
                    chat_id=chat_id,
                    text=text,
                    thread_id=thread_id,
                    photo=photo,
                )
            )

        # ==============================================
        # TELEGRAM TIMEOUT
        # ==============================================

        except TimedOut:

            logger.warning(
                "Telegram timeout"
            )

            await asyncio.sleep(3)

            return (
                await TelegramPublisher.publish(
                    bot=bot,
                    chat_id=chat_id,
                    text=text,
                    thread_id=thread_id,
                    photo=photo,
                )
            )

        # ==============================================
        # BAD REQUEST
        # ==============================================

        except BadRequest as exc:

            logger.error(
                f"BadRequest: {exc}"
            )

            raise

        # ==============================================
        # UNKNOWN ERROR
        # ==============================================

        except Exception as exc:

            logger.exception(
                f"Publish error: {exc}"
            )

            raise
