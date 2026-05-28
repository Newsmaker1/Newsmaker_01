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

from database.session import (
    AsyncSessionLocal,
)

from models.destination import (
    Destination,
)

from models.pack_destination import (
    PackDestination,
)

from models.source_pack import (
    SourcePack,
)

from keyboards.admin.routing_menu import (
    get_routing_menu,
)

from states.routing_state import (
    ROUTING_ADD_STATE,
)


ROUTING_BUTTON = (
    "🔀 Routing"
)


async def routing_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    if (
        update.message.text
        != ROUTING_BUTTON
    ):
        return

    await update.message.reply_text(
        text=(
            "🔀 Routing management\n\n"
            "Выберите действие:"
        ),
        reply_markup=get_routing_menu(),
    )


async def build_routing_text():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(PackDestination)
            .order_by(
                PackDestination.id.desc()
            )
        )

        routes = result.scalars().all()

    if not routes:

        return (
            "📭 Routing отсутствует",
            None,
        )

    text = "🔀 Routing list\n\n"

    keyboard = []

    for route in routes:

        text += (
            f"ID: {route.id}\n"
            f"PACK: {route.pack.name}\n"
            f"DESTINATION: "
            f"{route.destination.title}\n"
            f"ACTIVE: {route.is_active}\n\n"
        )

        toggle_text = (
            "🔴 Disable"
            if route.is_active
            else "🟢 Enable"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=(
                        f"routing_toggle_{route.id}"
                    ),
                ),
                InlineKeyboardButton(
                    text=f"❌ Delete #{route.id}",
                    callback_data=(
                        f"routing_delete_{route.id}"
                    ),
                ),
            ]
        )

    return (
        text[:4000],
        InlineKeyboardMarkup(keyboard),
    )


async def routing_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    print(
        "ROUTING CALLBACK:",
        data
    )

    # ==========================================
    # ADD
    # ==========================================

    if data == "routing_add":

        user_id = query.from_user.id

        ROUTING_ADD_STATE[user_id] = {
            "step": "waiting_pack_id"
        }

        await query.message.reply_text(
            text="Введите PACK ID:"
        )

        return

    # ==========================================
    # LIST
    # ==========================================

    if data == "routing_list":

        text, keyboard = (
            await build_routing_text()
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
        "routing_toggle_"
    ):

        route_id = int(
            data.replace(
                "routing_toggle_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            route = await session.get(
                PackDestination,
                route_id,
            )

            if not route:

                await query.message.reply_text(
                    text="❌ Routing не найден"
                )

                return

            route.is_active = (
                not route.is_active
            )

            await session.commit()

        text, keyboard = (
            await build_routing_text()
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
        "routing_delete_"
    ):

        route_id = int(
            data.replace(
                "routing_delete_",
                ""
            )
        )

        async with AsyncSessionLocal() as session:

            route = await session.get(
                PackDestination,
                route_id,
            )

            if not route:

                await query.message.reply_text(
                    text="❌ Routing не найден"
                )

                return

            await session.delete(route)

            await session.commit()

        text, keyboard = (
            await build_routing_text()
        )

        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

        return


async def add_routing_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    if user_id not in ROUTING_ADD_STATE:
        return

    state = ROUTING_ADD_STATE[user_id]

    # ==========================================
    # PACK ID
    # ==========================================

    if state["step"] == "waiting_pack_id":

        try:

            pack_id = int(
                update.message.text.strip()
            )

        except ValueError:

            del ROUTING_ADD_STATE[user_id]

            await update.message.reply_text(
                text="❌ PACK ID должен быть числом"
            )

            return

        async with AsyncSessionLocal() as session:

            pack = await session.get(
                SourcePack,
                pack_id,
            )

            if not pack:

                del ROUTING_ADD_STATE[user_id]

                await update.message.reply_text(
                    text="❌ PACK не найден"
                )

                return

        state["pack_id"] = pack_id

        state["step"] = "waiting_destination_id"

        await update.message.reply_text(
            text="Введите DESTINATION ID:"
        )

        return

    # ==========================================
    # DESTINATION ID
    # ==========================================

    if (
        state["step"]
        == "waiting_destination_id"
    ):

        try:

            destination_id = int(
                update.message.text.strip()
            )

        except ValueError:

            del ROUTING_ADD_STATE[user_id]

            await update.message.reply_text(
                text=(
                    "❌ DESTINATION ID "
                    "должен быть числом"
                )
            )

            return

        async with AsyncSessionLocal() as session:

            destination = await session.get(
                Destination,
                destination_id,
            )

            if not destination:

                del ROUTING_ADD_STATE[user_id]

                await update.message.reply_text(
                    text=(
                        "❌ DESTINATION "
                        "не найден"
                    )
                )

                return

            existing = await session.execute(
                select(PackDestination)
                .where(
                    PackDestination.pack_id
                    == state["pack_id"],
                    PackDestination.destination_id
                    == destination_id,
                )
            )

            existing_route = (
                existing.scalar_one_or_none()
            )

            if existing_route:

                del ROUTING_ADD_STATE[user_id]

                await update.message.reply_text(
                    text=(
                        "❌ Routing уже существует"
                    )
                )

                return

            route = PackDestination(
                pack_id=state["pack_id"],
                destination_id=destination_id,
                is_active=True,
            )

            session.add(route)

            await session.commit()

            await session.refresh(route)

        del ROUTING_ADD_STATE[user_id]

        await update.message.reply_text(
            text=(
                "✅ Routing создан\n\n"
                f"PACK: {route.pack_id}\n"
                f"DESTINATION: "
                f"{route.destination_id}"
            )
        )
