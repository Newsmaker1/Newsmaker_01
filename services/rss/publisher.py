import asyncio
import logging

from telegram.constants import ParseMode
from telegram.error import RetryAfter, TimedOut

from config.settings import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()


class TelegramPublisher:
    @staticmethod
    async def publish(
        bot,
        chat_id: int,
        text: str,
        thread_id: int | None = None,
        photo: str | None = None,
    ):
        try:
            await asyncio.sleep(
                settings.TELEGRAM_SEND_DELAY
            )

            if photo:
                message = await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    message_thread_id=thread_id,
                )
            else:
                message = await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False,
                    message_thread_id=thread_id,
                )

            logger.info(
                f"Message delivered "
                f"to {chat_id}"
            )

            return message

        except RetryAfter as exc:
            logger.warning(
                f"Flood control triggered: "
                f"{exc.retry_after}"
            )

            await asyncio.sleep(
                exc.retry_after
            )

            return await TelegramPublisher.publish(
                bot=bot,
                chat_id=chat_id,
                text=text,
                thread_id=thread_id,
                photo=photo,
            )

        except TimedOut:
            logger.warning(
                "Telegram timeout"
            )

            await asyncio.sleep(3)

            return await TelegramPublisher.publish(
                bot=bot,
                chat_id=chat_id,
                text=text,
                thread_id=thread_id,
                photo=photo,
            )

        except Exception as exc:
            logger.error(
                f"Publish error: {exc}"
            )

            raise
