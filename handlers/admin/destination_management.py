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

from models.destination import (
    Destination,
)

from models.enums import (
    DestinationType,
)

from bot.constants.buttons import (
    DESTINATIONS_BUTTON,
)

from keyboards.admin.destination_menu import (
    get_destination_menu,
)

from states.destination_state import (
    DESTINATION_ADD_STATE,
)

settings = get_settings()


async def destinations_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    if (
        update.message.text
        != DESTINATIONS_BUTTON
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
            "📬 Каналы публикации\n\n"
            "Выберите действие:"
        ),
        reply_markup=get_destination_menu(),
    )


async def build_destinations_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Destination)
            .where(
                Destination.is_deleted == False
            )
            .order_by(
                Destination.id.desc()
            )
        )

        destinations = (
            result.scalars().all()
        )

    if not destinations:

        return (
            "📭 Каналы публикации отсутствуют",
            None,
        )

    text = "📬 Список каналов\n\n"

    keyboard = []

    for dest in destinations:

        status = (
            "🟢 ACTIVE"
            if dest.is_active
            else "🔴 DISABLED"
        )

        text += (
            f"{status}\n"
            f"ID: {dest.id}\n"
            f"TITLE: {dest.title}\n"
            f"TYPE: {dest.type.value}\n"
            f"CHAT ID: "
            f"{dest.telegram_chat_id}\n\n"
        )

        toggle_text = (
            "🔴 Disable"
            if dest.is_active
            else "🟢 Enable"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=(
                        f"destination_toggle_{dest.id}"
                    ),
                ),
                InlineKeyboardButton(
                    text=f"❌ Delete #{dest.id}",
                    callback_data=(
                        f"destination_delete_{dest.id}"
                    ),
                ),
            ]
        )

    return (
        text[:4000],
        InlineKeyboardMarkup(keyboard),
    )


async def destination_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    print(
        "DESTINATION CALLBACK:",
        data
    )

    # ==========================================
    # ADD DESTINATION
    # ==========================================

    if data == "destination_add":

        user_id = query.from_user.id

        DESTINATION_ADD_STATE[user_id] = {
            "step": "waiting_type"
        }

        await query.message.reply_text(
            text=(
                "📬 Добавление канала\n\n"
                "Введите TYPE:\n\n"
                "channel\n"
                "group\n"
                "private\n"
                "forum_topic"
            )
        )

        return

    # ==========================================
    # LIST
    # ==========================================

    if data == "destination_list":

        text, keyboard = (
            await build_destinations_text()
        )

        await query.message.reply_text(
            text=text,
            reply_markup=keyboard,
        )

        return

    # ==========================================
    # TOGGLE
    # ==========================================

    if data.startswith(
        "destination_toggle_"
    ):

        destination_id = int(
            data.replace(
                "destination_toggle_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            destination = await session.get(
                Destination,
                destination_id,
            )

            if not destination:

                await query.message.reply_text(
                    text="❌ Destination не найден"
                )

                return

            destination.is_active = (
                not destination.is_active
            )

            await session.commit()

        text, keyboard = (
            await build_destinations_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return

    # ==========================================
    # DELETE
    # ==========================================

    if data.startswith(
        "destination_delete_"
    ):

        destination_id = int(
            data.replace(
                "destination_delete_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            destination = await session.get(
                Destination,
                destination_id,
            )

            if not destination:

                await query.message.reply_text(
                    text="❌ Destination не найден"
                )

                return

            destination.is_deleted = True

            await session.commit()

        text, keyboard = (
            await build_destinations_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return


async def add_destination_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    if user_id not in DESTINATION_ADD_STATE:
        return

    state = DESTINATION_ADD_STATE[user_id]

    # ==========================================
    # WAITING TYPE
    # ==========================================

    if state["step"] == "waiting_type":

        destination_type = (
            update.message.text.strip()
        )

        allowed_types = [
            item.value
            for item
            in DestinationType
        ]

        if (
            destination_type
            not in allowed_types
        ):

            del DESTINATION_ADD_STATE[user_id]

            await update.message.reply_text(
                text="❌ Неверный TYPE"
            )

            return

        state["type"] = destination_type

        state["step"] = "waiting_chat_id"

        await update.message.reply_text(
            text="Введите CHAT ID:"
        )

        return

    # ==========================================
    # WAITING CHAT ID
    # ==========================================

    if state["step"] == "waiting_chat_id":

        try:

            chat_id = int(
                update.message.text.strip()
            )

        except ValueError:

            del DESTINATION_ADD_STATE[user_id]

            await update.message.reply_text(
                text="❌ CHAT ID должен быть числом"
            )

            return

        state["chat_id"] = chat_id

        state["step"] = "waiting_title"

        await update.message.reply_text(
            text="Введите TITLE:"
        )

        return

    # ==========================================
    # WAITING TITLE
    # ==========================================

    if state["step"] == "waiting_title":

        title = (
            update.message.text.strip()
        )

        async with AsyncSessionLocal() as session:

            destination = Destination(
                user_id=user_id,
                type=DestinationType(
                    state["type"]
                ),
                telegram_chat_id=(
                    state["chat_id"]
                ),
                title=title,
                is_active=True,
            )

            session.add(destination)

            await session.commit()

            await session.refresh(destination)

        del DESTINATION_ADD_STATE[user_id]

        await update.message.reply_text(
            text=(
                "✅ Канал публикации создан\n\n"
                f"ID: {destination.id}\n"
                f"TITLE: {destination.title}"
            )
        )
