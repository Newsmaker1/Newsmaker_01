import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from database.session import (
    AsyncSessionLocal,
)
from models.source_pack import (
    PackSource,
)


logger = logging.getLogger(__name__)


async def rss_sources_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PackSource)
            .order_by(PackSource.id.desc())
            .limit(20)
        )

        sources = result.scalars().all()

    if not sources:
        text = (
            "📰 RSS источники\n\n"
            "Источников пока нет."
        )
    else:
        lines = [
            "📰 RSS источники\n"
        ]

        for source in sources:
            lines.append(
                f"ID: {source.id}\n"
                f"Pack: {source.pack_id}\n"
                f"URL: {source.source_url}\n"
                f"Active: {source.is_active}\n"
            )

        text = "\n".join(lines)

    text += (
        "\n\n"
        "Добавить источник:\n"
        "/add_rss URL PACK_ID"
    )

    await update.message.reply_text(
        text
    )


async def add_rss_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        args = context.args

        if len(args) < 2:
            await update.message.reply_text(
                "Использование:\n"
                "/add_rss RSS_URL PACK_ID"
            )

            return

        rss_url = args[0]
        pack_id = int(args[1])

        async with AsyncSessionLocal() as session:
            source = PackSource(
                pack_id=pack_id,
                source_url=rss_url,
                is_active=True,
            )

            session.add(source)

            await session.commit()

        await update.message.reply_text(
            "✅ RSS источник добавлен"
        )

        logger.info(
            f"RSS source added: "
            f"{rss_url}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            f"❌ Ошибка:\n{exc}"
        )
