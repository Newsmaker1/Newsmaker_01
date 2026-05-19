import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from database.session import (
    AsyncSessionLocal,
)
from models.destination import (
    Destination,
)
from models.enums import (
    DestinationType,
)


logger = logging.getLogger(__name__)


async def destinations_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Destination)
            .order_by(
                Destination.id.asc()
            )
        )

        destinations = (
            result.scalars().all()
        )

    if not destinations:
        text = (
            "📬 Destinations\n\n"
            "Destinations пока нет."
        )
    else:
        lines = [
            "📬 Destinations\n"
        ]

        for dest in destinations:
            lines.append(
                f"ID: {dest.id}\n"
                f"Title: {dest.title}\n"
                f"Type: {dest.type}\n"
                f"Chat ID: "
                f"{dest.telegram_chat_id}\n"
                f"Thread ID: "
                f"{dest.telegram_thread_id}\n"
                f"Active: "
                f"{dest.is_active}\n"
            )

        text = "\n".join(lines)

    text += (
        "\n\n"
        "Добавить destination:\n"
        "/add_destination "
        "TYPE CHAT_ID TITLE\n\n"
        "Типы:\n"
        "private\n"
        "channel\n"
        "group\n"
        "forum_topic"
    )

    await update.message.reply_text(
        text
    )


async def add_destination_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        args = context.args

        if len(args) < 3:
            await update.message.reply_text(
                "Использование:\n"
                "/add_destination "
                "TYPE CHAT_ID TITLE"
            )

            return

        destination_type = args[0]
        chat_id = int(args[1])

        title = " ".join(args[2:])

        allowed_types = [
            item.value
            for item
            in DestinationType
        ]

        if (
            destination_type
            not in allowed_types
        ):
            await update.message.reply_text(
                "❌ Неверный TYPE"
            )

            return

        async with AsyncSessionLocal() as session:
            destination = Destination(
                user_id=1,
                type=DestinationType(
                    destination_type
                ),
                telegram_chat_id=chat_id,
                title=title,
                is_active=True,
            )

            session.add(destination)

            await session.commit()

        await update.message.reply_text(
            "✅ Destination добавлен"
        )

        logger.info(
            f"Destination added: "
            f"{chat_id}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            f"❌ Ошибка:\n{exc}"
        )
