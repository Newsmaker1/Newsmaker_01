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

from models.source_type import (
    SourceType,
)

from keyboards.admin.rss_menu import (
    get_rss_menu,
)

from bot.constants.buttons import (
    RSS_SOURCES_BUTTON,
)

from states.rss_state import (
    RSS_ADD_STATE,
)

import traceback

logger = logging.getLogger(__name__)

settings = get_settings()


# ==================================================
# RSS MENU
# ==================================================

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

    # ==============================================
    # ACCESS CHECK
    # ==============================================

    if user.id not in settings.ADMIN_IDS:

        logger.warning(
            f"Unauthorized RSS access: "
            f"{user.id}"
        )

        await update.message.reply_text(
            text="⛔ Нет доступа",
        )

        return

    # ==============================================
    # OPEN MENU
    # ==============================================

    logger.info(
        f"RSS menu opened: "
        f"{user.id}"
    )

    await update.message.reply_text(

        text=(

            "📰 Управление источниками\n\n"

            "Выберите действие:"

        ),

        reply_markup=get_rss_menu(),
    )


# ==================================================
# BUILD RSS LIST
# ==================================================

async def build_rss_list_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(

            select(
                PackSource,
                SourcePack,
            )
            .join(
                SourcePack,
                SourcePack.id
                == PackSource.pack_id,
            )
            .order_by(
                PackSource.id.desc()
            )

        )

        rows = result.all()

    # ==============================================
    # EMPTY
    # ==============================================

    if not rows:

        return (
            "📭 RSS источники отсутствуют",
            None,
        )

    text = "📋 Список RSS\n\n"

    keyboard = []

    # ==============================================
    # BUILD LIST
    # ==============================================

    for source, pack in rows:

        status = (
            "🟢 ACTIVE"
            if source.is_active
            else "🔴 DISABLED"
        )

        text += (

            f"{status}\n"

            f"ID: "
            f"{source.id}\n"

            f"PACK: "
            f"{pack.name}\n"

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
                        f"rss_toggle_"
                        f"{source.id}"
                    ),
                ),

                InlineKeyboardButton(

                    text=(
                        f"❌ Delete "
                        f"#{source.id}"
                    ),

                    callback_data=(
                        f"rss_delete_"
                        f"{source.id}"
                    ),
                ),

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

async def rss_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    logger.warning(
        f"RSS CALLBACK: {query.data}"
    )
    
    data = query.data

    # ==========================================
    # ADD RSS
    # ==========================================

    if data == "rss_add":

        user_id = query.from_user.id

        if user_id in RSS_ADD_STATE:

            await query.message.reply_text(

                text=(

                    "⚠️ Вы уже "
                    "добавляете RSS.\n\n"

                    "Сначала завершите "
                    "текущий процесс."

                )

            )

            return

        RSS_ADD_STATE[user_id] = {
            "step": "waiting_url"
        }

        logger.info(
            f"RSS creation started: "
            f"{user_id}"
        )

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
    # SELECT PACK
    # ==========================================

    if data.startswith("rss_pack_"):
    
        logger.warning(
            f"RSS PACK SELECTED: {data}"
        )
    
        user_id = query.from_user.id
    
        logger.warning(
            f"RSS_ADD_STATE: "
            f"{RSS_ADD_STATE}"
        )
    
        if user_id not in RSS_ADD_STATE:
    
            logger.warning(
                f"RSS SESSION NOT FOUND "
                f"FOR USER {user_id}"
            )
    
            await query.message.reply_text(
    
                text=(
    
                    "❌ Сессия истекла.\n\n"
    
                    "Начните заново."
    
                )
    
            )
    
            return
    
        state = RSS_ADD_STATE[user_id]
    
        logger.warning(
            f"RSS STATE: {state}"
        )
    
        if "rss_url" not in state:
    
            logger.warning(
                "RSS URL MISSING IN STATE"
            )
    
            del RSS_ADD_STATE[user_id]
    
            await query.message.reply_text(
    
                text=(
    
                    "❌ RSS URL отсутствует.\n\n"
    
                    "Начните заново."
    
                )
    
            )
    
            return
    
        pack_id = int(
            data.replace(
                "rss_pack_",
                ""
            )
        )
    
        logger.warning(
            f"PACK ID SELECTED: "
            f"{pack_id}"
        )
    
        try:
    
            async with AsyncSessionLocal() as session:
    
                pack = await session.get(
                    SourcePack,
                    pack_id,
                )
    
                logger.warning(
                    f"PACK FOUND: {pack}"
                )
    
                if not pack:
    
                    del RSS_ADD_STATE[user_id]
    
                    await query.message.reply_text(
    
                        text=(
    
                            "❌ PACK не найден.\n\n"
    
                            "Начните заново."
    
                        )
    
                    )
    
                    return
    
                logger.warning(
                    f"CREATING RSS: "
                    f"{state['rss_url']}"
                )
    
                source = PackSource(
                
                    pack_id=pack.id,
                
                    source_url=(
                        state["rss_url"]
                    ),
                
                    is_active=True,
                
                    source_type=SourceType.RSS,
                )

                logger.warning(
                    f"PACK ID={pack.id}"
                )
                
                logger.warning(
                    f"RSS URL={state['rss_url']}"
                )
                
                logger.warning(
                    f"SOURCE TYPE={SourceType.RSS}"
                )
                
                session.add(source)
    
                logger.warning(
                    "BEFORE COMMIT"
                )
    
                await session.commit()
    
                logger.warning(
                    "AFTER COMMIT"
                )
    
                await session.refresh(source)
    
                logger.warning(
                    f"RSS CREATED: "
                    f"{source.id}"
                )
    
        except Exception as exc:
    
            logger.error(
                "RSS CREATE ERROR FULL:\n%s",
                traceback.format_exc(),
            )
    
            await query.message.reply_text(
    
                text=(
    
                    "❌ Ошибка создания RSS.\n\n"
    
                    "Смотрите лог Railway."
    
                )
    
            )
    
            return
    
        del RSS_ADD_STATE[user_id]
    
        logger.info(
            f"RSS added: "
            f"{source.id}"
        )
    
        await query.message.reply_text(
    
            text=(
    
                "✅ RSS успешно добавлен\n\n"
    
                f"ID: "
                f"{source.id}\n"
    
                f"PACK: "
                f"{pack.name}\n\n"
    
                f"{source.source_url}"
    
            )
    
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

        logger.info(
            f"RSS toggled: "
            f"{source_id}"
        )

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

        logger.info(
            f"RSS deleted: "
            f"{source_id}"
        )

        text, keyboard = (
            await build_rss_list_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return


# ==================================================
# ADD RSS FSM
# ==================================================

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

        rss_url = (
            update.message.text.strip()
        )

        # ======================================
        # VALIDATION
        # ======================================

        if not rss_url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            del RSS_ADD_STATE[user_id]

            await update.message.reply_text(

                text=(

                    "❌ Некорректный URL\n\n"

                    "Начните добавление "
                    "заново."

                )

            )

            return

        async with AsyncSessionLocal() as session:

            result = await session.execute(

                select(SourcePack)
                .where(
                    SourcePack.is_deleted.is_(
                        False
                    )
                )
                .order_by(
                    SourcePack.id.asc()
                )

            )

            packs = (
                result.scalars().all()
            )

        # ======================================
        # NO PACKS
        # ======================================

        if not packs:

            del RSS_ADD_STATE[user_id]

            await update.message.reply_text(

                text=(

                    "❌ Нет доступных "
                    "пакетов.\n\n"

                    "Сначала создайте "
                    "пакет."

                )

            )

            return

        state["rss_url"] = rss_url

        state["step"] = "waiting_pack"

        # ======================================
        # PACK SELECTOR
        # ======================================

        keyboard = []

        for pack in packs:

            keyboard.append(

                [

                    InlineKeyboardButton(

                        text=(
                            f"📦 "
                            f"{pack.name}"
                        ),

                        callback_data=(
                            f"rss_pack_"
                            f"{pack.id}"
                        ),
                    )

                ]

            )

        await update.message.reply_text(

            text=(

                "📦 Выберите пакет "
                "для RSS:"

            ),

            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
        )

        return
