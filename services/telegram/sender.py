import asyncio
import logging

from telegram import (
    Bot,
)

from telegram.error import (
    RetryAfter,
    TimedOut,
    TelegramError,
)

from config.settings import (
    get_settings,
)

settings = get_settings()

logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.BOT_TOKEN
)


async def send_message(
    chat_id: int,
    text: str,
    thread_id: int | None = None,
):

    try:

        await asyncio.sleep(
            settings.TELEGRAM_SEND_DELAY
        )

        await bot.send_message(
            chat_id=chat_id,
            text=text[:4096],
            message_thread_id=thread_id,
            disable_web_page_preview=False,
        )

        logger.info(
            f"Message sent to {chat_id}"
        )

        return True

    # ==========================================
    # FLOOD CONTROL
    # ==========================================

    except RetryAfter as exc:

        logger.warning(
            f"Flood control: "
            f"sleep {exc.retry_after}"
        )

        await asyncio.sleep(
            exc.retry_after
        )

        return await send_message(
            chat_id=chat_id,
            text=text,
            thread_id=thread_id,
        )

    # ==========================================
    # TIMEOUT
    # ==========================================

    except TimedOut:

        logger.warning(
            f"Timeout sending to {chat_id}"
        )

        return False

    # ==========================================
    # TELEGRAM ERROR
    # ==========================================

    except TelegramError as exc:

        logger.exception(exc)

        return False

    # ==========================================
    # UNKNOWN ERROR
    # ==========================================

    except Exception as exc:

        logger.exception(exc)

        return False
