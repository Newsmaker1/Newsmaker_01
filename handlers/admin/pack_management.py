import logging

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


logger = logging.getLogger(__name__)

settings = get_settings()


# ==================================================
# PACKS MENU
# ==================================================

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

    # ==============================================
    # ACCESS CHECK
    # ==============================================

    if user.id not in settings.ADMIN_IDS:

        logger.warning(
            f"Unauthorized packs access: "
            f"{user.id}"
        )

        await update.message.reply_text(
            text="⛔ Нет доступа"
        )

        return

    # ==============================================
    # OPEN MENU
    # ==============================================

    logger.info(
        f"Pack menu opened: "
        f"{user.id}"
    )

    await update.message.reply_text(

        text=(

            "📦 Управление пакетами\n\n"

            "Выберите действие:"

        ),

        reply_markup=get_packs_menu(),
    )


# ==================================================
# BUILD PACKS LIST
# ==================================================

async def build_packs_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(SourcePack)
            .where(
                SourcePack.is_deleted.is_(
                    False
                )
            )
            .order_by(
                SourcePack.id.desc()
            )
        )

        packs = result.scalars().all()

        if not packs:

            return (
                "📭 Пакеты отсутствуют",
                None,
            )

        text = "📦 Список пакетов\n\n"

        keyboard = []

        for pack in packs:

            count_result = await session.execute(

                select(
                    func.count(
                        PackSource.id
                    )
                ).where(
                    PackSource.pack_id
                    == pack.id
                )

            )

            rss_count = (
                count_result.scalar()
            )

            text += (

                f"📦 #{pack.id}\n"

                f"Название: "
                f"{pack.name}\n"

                f"Источников: "
                f"{rss_count}\n\n"

            )

            keyboard.append(

                [

                    InlineKeyboardButton(

                        text=(
                            f"❌ Удалить "
                            f"#{pack.id}"
                        ),

                        callback_data=(
                            f"pack_delete_"
                            f"{pack.id}"
                        ),
                    )

                ]

            )

    return (
        text[:4000],
        InlineKeyboardMarkup(
            keyboard
        ),
    )


# ==================================================
# CALLBACK HANDLER
# ==================================================

async def pack_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    # ==========================================
    # ADD PACK
    # ==========================================

    if data == "pack_add":

        user_id = query.from_user.id

        if user_id in PACK_ADD_STATE:

            await query.message.reply_text(

                text=(
                    "⚠️ Вы уже "
                    "создаёте пакет."
                )

            )

            return

        PACK_ADD_STATE[user_id] = {
            "step": "waiting_name"
        }

        logger.info(
            f"Pack creation started: "
            f"{user_id}"
        )

        await query.message.reply_text(

            text=(

                "📦 Создание пакета\n\n"

                "Введите название пакета:"

            )

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

                select(
                    func.count(
                        PackSource.id
                    )
                ).where(
                    PackSource.pack_id
                    == pack_id
                )

            )

            rss_count = (
                rss_result.scalar()
            )

            # ======================================
            # RSS EXISTS
            # ======================================

            if rss_count > 0:

                await query.message.reply_text(

                    text=(

                        "❌ Нельзя удалить пакет.\n\n"

                        "Сначала удалите "
                        "источники."

                    )

                )

                return

            pack = await session.get(
                SourcePack,
                pack_id,
            )

            # ======================================
            # NOT FOUND
            # ======================================

            if not pack:

                await query.message.reply_text(
                    text="❌ Пакет не найден"
                )

                return

            # ======================================
            # SOFT DELETE
            # ======================================

            pack.is_deleted = True

            await session.commit()

            logger.info(
                f"Pack deleted: "
                f"{pack_id}"
            )

        text, keyboard = (
            await build_packs_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return


# ==================================================
# ADD PACK FSM
# ==================================================

async def add_pack_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    logger.warning(
        f"ADD_PACK_HANDLER CALLED | "
        f"text={getattr(update.message, 'text', None)!r}"
    )

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    logger.warning(
        f"PACK_ADD_STATE={PACK_ADD_STATE}"
    )

    if user_id not in PACK_ADD_STATE:

        logger.warning(
            f"USER {user_id} "
            f"NOT IN PACK_ADD_STATE"
        )

        return

    state = PACK_ADD_STATE[user_id]

    logger.warning(
        f"PACK FSM STATE={state}"
    )

    # ==========================================
    # WAITING NAME
    # ==========================================

    if state["step"] == "waiting_name":

        pack_name = (
            update.message.text.strip()
        )

        logger.warning(
            f"CREATING PACK: {pack_name}"
        )

        # ======================================
        # VALIDATION
        # ======================================

        if len(pack_name) < 2:

            del PACK_ADD_STATE[user_id]

            await update.message.reply_text(

                text=(

                    "❌ Слишком короткое "
                    "название."

                )

            )

            return

        try:

            async with AsyncSessionLocal() as session:

                # ==================================
                # DUPLICATE CHECK
                # ==================================

                result = await session.execute(

                    select(SourcePack).where(
                        SourcePack.name
                        == pack_name
                    )

                )

                existing_pack = (
                    result.scalar_one_or_none()
                )

                if existing_pack:

                    del PACK_ADD_STATE[user_id]

                    await update.message.reply_text(

                        text=(

                            "❌ Пакет с таким "
                            "названием уже "
                            "существует."

                        )

                    )

                    return

                # ==================================
                # CREATE PACK
                # ==================================

                pack = SourcePack(
                    name=pack_name,
                    slug=pack_name.lower()
                    .replace(" ", "-"),
                )

                session.add(pack)

                await session.commit()

                await session.refresh(pack)

                logger.warning(
                    f"PACK CREATED: "
                    f"id={pack.id}"
                )

        except Exception as exc:

            logger.exception(
                f"PACK CREATE ERROR: "
                f"{exc}"
            )

            await update.message.reply_text(
                text=(
                    "❌ Ошибка создания "
                    "пакета. Смотри лог."
                )
            )

            return

        del PACK_ADD_STATE[user_id]

        logger.info(
            f"Pack created: "
            f"{pack.id}"
        )

        await update.message.reply_text(

            text=(

                "✅ Пакет создан\n\n"

                f"ID: "
                f"{pack.id}\n"

                f"Название: "
                f"{pack.name}"

            )

        )
