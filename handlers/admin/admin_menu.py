from telegram import Update

from telegram.ext import (
    ContextTypes,
)

from config.settings import (
    get_settings,
)

from keyboards.admin.admin_menu import (
    get_admin_menu,
)

from bot.constants.buttons import (
    ADMIN_BUTTON,
)


async def admin_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    print(
        "ADMIN BUTTON:",
        repr(update.message.text)
    )

    if (
        update.message.text
        != ADMIN_BUTTON
    ):
        return

    settings = get_settings()

    user = update.effective_user

    if user is None:
        return

    print(
        "USER ID:",
        user.id
    )

    print(
        "ADMIN IDS:",
        settings.ADMIN_IDS
    )

    if user.id not in settings.ADMIN_IDS:
        await update.message.reply_text(
            text="⛔ Нет доступа",
        )

        return

    await update.message.reply_text(
        text=(
            "🛠 Панель администратора\n\n"
            "Выберите действие:"
        ),
        reply_markup=get_admin_menu(),
    )
