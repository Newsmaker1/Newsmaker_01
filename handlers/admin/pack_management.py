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
    SourcePack,
)

from bot.constants.buttons import (
    SOURCE_PACKS_BUTTON,
)

logger = logging.getLogger(__name__)


async def source_packs_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SourcePack)
            .order_by(SourcePack.id.asc())
        )

        packs = result.scalars().all()
    
    if (
        update.message.text
        != SOURCE_PACKS_BUTTON
    ):
        return
    
    # ==============================================
    # EMPTY LIST
    # ==============================================

    if not packs:
        text = (
            "📦 Пакеты источников\n\n"
            "Пакетов пока нет."
        )

    # ==============================================
    # PACKS LIST
    # ==============================================

    else:
        lines = [
            "📦 Пакеты источников\n"
        ]

        for pack in packs:
            lines.append(
                f"ID: {pack.id}\n"
                f"Название: {pack.name}\n"
                f"Slug: {pack.slug}\n"
                f"Активен: "
                f"{pack.is_active}\n"
            )

        text = "\n".join(lines)

    # ==============================================
    # HELP
    # ==============================================

    text += (
        "\n\n"
        "Создать пакет:\n"
        "/add_pack NAME SLUG"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=(
            get_admin_menu()
        ),
    )


async def add_pack_handler(
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
                    "/add_pack NAME SLUG"
                ),
                reply_markup=(
                    get_admin_menu()
                ),
            )

            return

        name = args[0]

        slug = args[1]

        # ==========================================
        # CHECK DUPLICATE
        # ==========================================

        async with AsyncSessionLocal() as session:
            existing = await session.execute(
                select(SourcePack).where(
                    SourcePack.slug == slug
                )
            )

            if existing.scalar_one_or_none():
                await update.message.reply_text(
                    text=(
                        "❌ Такой slug "
                        "уже существует"
                    ),
                    reply_markup=(
                        get_admin_menu()
                    ),
                )

                return

            # ======================================
            # CREATE PACK
            # ======================================

            pack = SourcePack(
                name=name,
                slug=slug,
                is_active=True,
            )

            session.add(pack)

            await session.commit()

        await update.message.reply_text(
            text=(
                "✅ Пакет создан\n\n"
                f"Название: {name}\n"
                f"Slug: {slug}"
            ),
            reply_markup=(
                get_admin_menu()
            ),
        )

        logger.info(
            f"Pack created: {slug}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            text=f"❌ Ошибка:\n{exc}",
            reply_markup=(
                get_admin_menu()
            ),
        )
