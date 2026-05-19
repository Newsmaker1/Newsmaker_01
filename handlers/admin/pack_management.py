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
    SourcePack,
)


logger = logging.getLogger(__name__)


async def source_packs_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SourcePack)
            .order_by(SourcePack.id.asc())
        )

        packs = result.scalars().all()

    if not packs:
        text = (
            "📦 Source Packs\n\n"
            "Паков пока нет."
        )
    else:
        lines = [
            "📦 Source Packs\n"
        ]

        for pack in packs:
            lines.append(
                f"ID: {pack.id}\n"
                f"Name: {pack.name}\n"
                f"Slug: {pack.slug}\n"
                f"Active: {pack.is_active}\n"
            )

        text = "\n".join(lines)

    text += (
        "\n\n"
        "Создать пак:\n"
        "/add_pack NAME SLUG"
    )

    await update.message.reply_text(
        text
    )


async def add_pack_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        args = context.args

        if len(args) < 2:
            await update.message.reply_text(
                "Использование:\n"
                "/add_pack NAME SLUG"
            )

            return

        name = args[0]
        slug = args[1]

        async with AsyncSessionLocal() as session:
            existing = await session.execute(
                select(SourcePack).where(
                    SourcePack.slug == slug
                )
            )

            if existing.scalar_one_or_none():
                await update.message.reply_text(
                    "❌ Такой slug уже существует"
                )

                return

            pack = SourcePack(
                name=name,
                slug=slug,
                is_active=True,
            )

            session.add(pack)

            await session.commit()

        await update.message.reply_text(
            f"✅ Pack создан\n\n"
            f"Name: {name}\n"
            f"Slug: {slug}"
        )

        logger.info(
            f"Pack created: {slug}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            f"❌ Ошибка:\n{exc}"
        )
