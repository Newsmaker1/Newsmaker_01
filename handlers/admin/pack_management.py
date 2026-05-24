from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from sqlalchemy import (
    func,
    select,
)

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
    SOURCE_PACKS_BUTTON,
)

from keyboards.admin.packs_menu import (
    get_packs_menu,
)

from states.pack_state import (
    PACK_ADD_STATE,
)

settings = get_settings()


async def source_packs_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    if (
        update.message.text
        != SOURCE_PACKS_BUTTON
    ):
        return

    user = update.effective_user

    if user is None:
        return

    if user.id not in settings.ADMIN_IDS:

        await update.message.reply_text(
            text="⛔ Нет доступа"
        )

        return

    await update.message.reply_text(
        text=(
            "📦 Управление PACKS\n\n"
            "Выберите действие:"
        ),
        reply_markup=get_packs_menu(),
    )


async def build_packs_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(SourcePack)
            .order_by(SourcePack.id.desc())
        )

        packs = result.scalars().all()

    if not packs:

        return (
            "📭 PACKS отсутствуют",
            None,
        )

    text = "📦 Список PACKS\n\n"

    keyboard = []

    async with AsyncSessionLocal() as session:

        for pack in packs:

            count_result = await session.execute(
                select(func.count(PackSource.id))
                .where(
                    PackSource.pack_id == pack.id
                )
            )

            rss_count = count_result.scalar()

            text += (
                f"📦 PACK #{pack.id}\n"
                f"NAME: {pack.name}\n"
                f"RSS: {rss_count}\n\n"
            )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"❌ Delete #{pack.id}",
                        callback_data=(
                            f"pack_delete_{pack.id}"
                        ),
                    )
                ]
            )

    return (
        text[:4000],
        InlineKeyboardMarkup(keyboard),
    )


async def pack_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    print(
        "PACK CALLBACK:",
        data
    )

    # ==========================================
    # ADD PACK
    # ==========================================

    if data == "pack_add":

        user_id = query.from_user.id

        if user_id in PACK_ADD_STATE:

            await query.message.reply_text(
                text=(
                    "⚠️ Вы уже создаёте PACK"
                )
            )

            return

        PACK_ADD_STATE[user_id] = {
            "step": "waiting_name"
        }

        await query.message.reply_text(
            text="📦 Введите название PACK:"
        )

        return

    # ==========================================
    # PACK LIST
    # ==========================================

    if data == "pack_list":

        text, keyboard = (
            await build_packs_text()
        )

        await query.message.reply_text(
            text=text,
            reply_markup=keyboard,
        )

        return

    # ==========================================
    # DELETE PACK
    # ==========================================

    if data.startswith("pack_delete_"):

        pack_id = int(
            data.replace(
                "pack_delete_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            rss_result = await session.execute(
                select(func.count(PackSource.id))
                .where(
                    PackSource.pack_id == pack_id
                )
            )

            rss_count = rss_result.scalar()

            if rss_count > 0:

                await query.message.reply_text(
                    text=(
                        "❌ Нельзя удалить PACK.\n\n"
                        "Сначала удалите RSS."
                    )
                )

                return

            pack = await session.get(
                SourcePack,
                pack_id,
            )

            if not pack:

                await query.message.reply_text(
                    text="❌ PACK не найден"
                )

                return

            await session.delete(pack)

            await session.commit()

        text, keyboard = (
            await build_packs_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return


async def add_pack_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    if user_id not in PACK_ADD_STATE:
        return

    state = PACK_ADD_STATE[user_id]

    if state["step"] == "waiting_name":

        pack_name = (
            update.message.text.strip()
        )

        if len(pack_name) < 2:

            del PACK_ADD_STATE[user_id]

            await update.message.reply_text(
                text=(
                    "❌ Слишком короткое имя"
                )
            )

            return

        async with AsyncSessionLocal() as session:

            pack = SourcePack(
                name=pack_name,
            )

            session.add(pack)

            await session.commit()

            await session.refresh(pack)

        del PACK_ADD_STATE[user_id]

        await update.message.reply_text(
            text=(
                "✅ PACK создан\n\n"
                f"ID: {pack.id}\n"
                f"NAME: {pack.name}"
            )
        )
