from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from sqlalchemy import select

from config.settings import (
    get_settings,
)

from database.session import (
    AsyncSessionLocal,
)

from models.source_pack import (
    PackSource,
)

from bot.constants.buttons import (
    RSS_SOURCES_BUTTON,
)

from keyboards.admin.rss_menu import (
    get_rss_menu,
)

settings = get_settings()


async def rss_sources_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    print(
        "RSS BUTTON:",
        repr(update.message.text)
    )

    if (
        update.message.text
        != RSS_SOURCES_BUTTON
    ):
        return

    user = update.effective_user

    if user is None:
        return

    if user.id not in settings.ADMIN_IDS:
        await update.message.reply_text(
            text="⛔ Нет доступа",
        )

        return

    await update.message.reply_text(
        text=(
            "📰 Управление RSS\n\n"
            "Выберите действие:"
        ),
        reply_markup=get_rss_menu(),
    )


async def rss_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    print(
        "RSS CALLBACK:",
        data
    )

    # ==========================================
    # ADD RSS
    # ==========================================

    if data == "rss_add":

        await query.message.reply_text(
            text=(
                "➕ Добавление RSS\n\n"
                "Используйте команду:\n\n"
                "/add_rss RSS_URL PACK_ID"
            )
        )

        return

    # ==========================================
    # RSS LIST
    # ==========================================

    if data == "rss_list":

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(PackSource)
                .order_by(PackSource.id.desc())
            )

            sources = result.scalars().all()

        if not sources:

            await query.message.reply_text(
                text="📭 RSS источники отсутствуют"
            )

            return

        text = "📋 Список RSS\n\n"

        keyboard = []

        for source in sources:

            status = (
                "🟢"
                if source.is_active
                else "🔴"
            )

            text += (
                f"{status} ID: {source.id}\n"
                f"PACK: {source.pack_id}\n"
                f"{source.source_url}\n\n"
            )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"❌ Удалить #{source.id}",
                        callback_data=(
                            f"rss_delete_{source.id}"
                        ),
                    )
                ]
            )

        await query.message.reply_text(
            text=text[:4000],
            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
        )

        return

    # ==========================================
    # DELETE RSS
    # ==========================================

    if data.startswith("rss_delete_"):

        source_id = int(
            data.replace(
                "rss_delete_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            source = await session.get(
                PackSource,
                source_id,
            )

            if not source:

                await query.message.reply_text(
                    text="❌ RSS не найден"
                )

                return

            await session.delete(source)

            await session.commit()

        await query.message.reply_text(
            text=(
                f"✅ RSS #{source_id} удалён"
            )
        )

        return

    # ==========================================
    # REFRESH
    # ==========================================

    if data == "rss_refresh":

        await query.message.reply_text(
            text="🔄 RSS список обновлён"
        )

        return


async def add_rss_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    await update.message.reply_text(
        text=(
            "⚙️ Старый режим add_rss пока активен.\n\n"
            "Позже заменим на FSM форму."
        )
    )
