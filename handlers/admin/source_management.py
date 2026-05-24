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
    SourcePack,
)

from bot.constants.buttons import (
    RSS_SOURCES_BUTTON,
)

from keyboards.admin.rss_menu import (
    get_rss_menu,
)

from states.rss_state import (
    RSS_ADD_STATE,
)

settings = get_settings()


async def rss_sources_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

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


async def build_rss_list_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(PackSource)
            .order_by(PackSource.id.desc())
        )

        sources = result.scalars().all()

    if not sources:

        return (
            "📭 RSS источники отсутствуют",
            None,
        )

    text = "📋 Список RSS\n\n"

    keyboard = []

    for source in sources:

        status = (
            "🟢 ACTIVE"
            if source.is_active
            else "🔴 DISABLED"
        )

        text += (
            f"{status}\n"
            f"ID: {source.id}\n"
            f"PACK: {source.pack_id}\n"
            f"{source.source_url}\n\n"
        )

        toggle_text = (
            "🔴 Disable"
            if source.is_active
            else "🟢 Enable"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=(
                        f"rss_toggle_{source.id}"
                    ),
                ),
                InlineKeyboardButton(
                    text=f"❌ Delete #{source.id}",
                    callback_data=(
                        f"rss_delete_{source.id}"
                    ),
                ),
            ]
        )

    return (
        text[:4000],
        InlineKeyboardMarkup(keyboard),
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

        user_id = query.from_user.id

        if user_id in RSS_ADD_STATE:

            await query.message.reply_text(
                text=(
                    "⚠️ Вы уже добавляете RSS.\n\n"
                    "Сначала завершите текущий процесс."
                )
            )

            return

        RSS_ADD_STATE[user_id] = {
            "step": "waiting_url"
        }

        await query.message.reply_text(
            text=(
                "➕ Добавление RSS\n\n"
                "Введите RSS URL:"
            )
        )

        return

    # ==========================================
    # RSS LIST
    # ==========================================

    if data == "rss_list":

        text, keyboard = (
            await build_rss_list_text()
        )

        await query.message.reply_text(
            text=text,
            reply_markup=keyboard,
        )

        return

    # ==========================================
    # TOGGLE RSS
    # ==========================================

    if data.startswith("rss_toggle_"):

        source_id = int(
            data.replace(
                "rss_toggle_",
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

            source.is_active = (
                not source.is_active
            )

            await session.commit()

        text, keyboard = (
            await build_rss_list_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
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

        text, keyboard = (
            await build_rss_list_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return

    # ==========================================
    # REFRESH
    # ==========================================

    if data == "rss_refresh":

        text, keyboard = (
            await build_rss_list_text()
        )

        await query.message.reply_text(
            text=text,
            reply_markup=keyboard,
        )

        return


async def add_rss_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    if user_id not in RSS_ADD_STATE:
        return

    state = RSS_ADD_STATE[user_id]

    # ==========================================
    # WAITING URL
    # ==========================================

    if state["step"] == "waiting_url":

        rss_url = update.message.text.strip()

        if not rss_url.startswith(
            ("http://", "https://")
        ):

            del RSS_ADD_STATE[user_id]

            await update.message.reply_text(
                text=(
                    "❌ Некорректный URL\n\n"
                    "Начните добавление заново."
                )
            )

            return

        state["rss_url"] = rss_url

        state["step"] = "waiting_pack"

        await update.message.reply_text(
            text="📦 Теперь введите PACK ID:"
        )

        return

    # ==========================================
    # WAITING PACK
    # ==========================================

    if state["step"] == "waiting_pack":

        try:

            pack_id = int(
                update.message.text.strip()
            )

        except ValueError:

            del RSS_ADD_STATE[user_id]

            await update.message.reply_text(
                text=(
                    "❌ PACK ID должен быть числом\n\n"
                    "Начните добавление заново."
                )
            )

            return

        rss_url = state["rss_url"]

        async with AsyncSessionLocal() as session:

            pack = await session.get(
                SourcePack,
                pack_id,
            )

            if not pack:

                del RSS_ADD_STATE[user_id]

                await update.message.reply_text(
                    text=(
                        "❌ PACK ID не существует\n\n"
                        "Начните добавление заново."
                    )
                )

                return

            source = PackSource(
                pack_id=pack_id,
                source_url=rss_url,
                is_active=True,
            )

            session.add(source)

            await session.commit()

            await session.refresh(source)

        del RSS_ADD_STATE[user_id]

        await update.message.reply_text(
            text=(
                "✅ RSS успешно добавлен\n\n"
                f"ID: {source.id}\n"
                f"PACK: {source.pack_id}\n"
                f"{source.source_url}"
            )
        )
