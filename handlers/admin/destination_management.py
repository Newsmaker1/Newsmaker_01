import logging

from sqlalchemy import select

from telegram import Update

from telegram.ext import (
    ContextTypes,
)

from database.session import (
    AsyncSessionLocal,
)

from keyboards.admin.admin_menu import (
    get_admin_menu,
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
) -> None:
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

    # ==============================================
    # EMPTY LIST
    # ==============================================

    if not destinations:
        text = (
            "📬 Каналы публикации\n\n"
            "Каналы публикации "
            "пока не созданы."
        )

    # ==============================================
    # DESTINATIONS LIST
    # ==============================================

    else:
        lines = [
            "📬 Каналы публикации\n"
        ]

        for dest in destinations:
            lines.append(
                f"ID: {dest.id}\n"
                f"Название: "
                f"{dest.title}\n"
                f"Тип: {dest.type}\n"
                f"Chat ID: "
                f"{dest.telegram_chat_id}\n"
                f"Thread ID: "
                f"{dest.telegram_thread_id}\n"
                f"Активен: "
                f"{dest.is_active}\n"
            )

        text = "\n".join(lines)

    # ==============================================
    # HELP
    # ==============================================

    text += (
        "\n\n"
        "Добавить канал:\n"
        "/add_destination "
        "TYPE CHAT_ID TITLE\n\n"
        "Типы:\n"
        "private\n"
        "channel\n"
        "group\n"
        "forum_topic"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=(
            get_admin_menu()
        ),
    )


async def add_destination_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        args = context.args

        # ==========================================
        # VALIDATION
        # ==========================================

        if len(args) < 3:
            await update.message.reply_text(
                text=(
                    "Использование:\n"
                    "/add_destination "
                    "TYPE CHAT_ID TITLE"
                ),
                reply_markup=(
                    get_admin_menu()
                ),
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

        # ==========================================
        # TYPE VALIDATION
        # ==========================================

        if (
            destination_type
            not in allowed_types
        ):
            await update.message.reply_text(
                text="❌ Неверный TYPE",
                reply_markup=(
                    get_admin_menu()
                ),
            )

            return

        # ==========================================
        # CREATE DESTINATION
        # ==========================================

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
            text=(
                "✅ Канал публикации "
                "добавлен"
            ),
            reply_markup=(
                get_admin_menu()
            ),
        )

        logger.info(
            f"Destination added: "
            f"{chat_id}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            text=f"❌ Ошибка:\n{exc}",
            reply_markup=(
                get_admin_menu()
            ),
        )
