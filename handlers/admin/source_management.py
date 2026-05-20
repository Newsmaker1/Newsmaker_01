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

from models.source_pack import (
    PackSource,
)

from bot.constants.buttons import (
    RSS_SOURCES_BUTTON,
)

logger = logging.getLogger(__name__)


async def rss_sources_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    print(
        "RSS BUTTON:",
        repr(update.message.text)
    )

    if (
        update.message.text
        != RSS_SOURCES_BUTTON
    ):
        return
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PackSource)
            .order_by(
                PackSource.id.desc()
            )
            .limit(20)
        )

        sources = (
            result.scalars().all()
        )

    # ==============================================
    # EMPTY LIST
    # ==============================================

    if not sources:
        text = (
            "📰 RSS источники\n\n"
            "Источников пока нет."
        )

    # ==============================================
    # SOURCES LIST
    # ==============================================

    else:
        lines = [
            "📰 RSS источники\n"
        ]

        for source in sources:
            lines.append(
                f"ID: {source.id}\n"
                f"Пакет: {source.pack_id}\n"
                f"URL: {source.source_url}\n"
                f"Активен: "
                f"{source.is_active}\n"
            )

        text = "\n".join(lines)

    # ==============================================
    # HELP
    # ==============================================

    text += (
        "\n\n"
        "Добавить источник:\n"
        "/add_rss URL PACK_ID"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=(
            get_admin_menu()
        ),
    )


async def add_rss_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        args = context.args

        # ==========================================
        # VALIDATION
        # ==========================================

        if len(args) < 2:
            await update.message.reply_text(
                text=(
                    "Использование:\n"
                    "/add_rss "
                    "RSS_URL PACK_ID"
                ),
                reply_markup=(
                    get_admin_menu()
                ),
            )

            return

        rss_url = args[0]

        pack_id = int(args[1])

        # ==========================================
        # CREATE SOURCE
        # ==========================================

        async with AsyncSessionLocal() as session:
            source = PackSource(
                pack_id=pack_id,
                source_url=rss_url,
                is_active=True,
            )

            session.add(source)

            await session.commit()

        await update.message.reply_text(
            text="✅ RSS источник добавлен",
            reply_markup=(
                get_admin_menu()
            ),
        )

        logger.info(
            f"RSS source added: "
            f"{rss_url}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            text=f"❌ Ошибка:\n{exc}",
            reply_markup=(
                get_admin_menu()
            ),
        )
