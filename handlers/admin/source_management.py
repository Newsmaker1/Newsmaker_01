from telegram import (
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from config.settings import (
    get_settings,
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

    if data == "rss_add":

        await query.message.reply_text(
            text=(
                "➕ Добавление RSS\n\n"
                "Используйте:\n"
                "/add_rss RSS_URL PACK_ID"
            )
        )

        return

    if data == "rss_list":

        await query.message.reply_text(
            text=(
                "📋 Список RSS\n\n"
                "Скоро здесь появится "
                "полноценный список RSS."
            )
        )

        return

    if data == "rss_refresh":

        await query.message.reply_text(
            text="🔄 RSS список обновлён"
        )

        return


async def add_rss_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Старый handler пока оставляем.
    Позже заменим на FSM.
    """

    await update.message.reply_text(
        text=(
            "⚙️ Старый режим add_rss пока активен.\n\n"
            "Позже заменим на FSM форму."
        )
    )
