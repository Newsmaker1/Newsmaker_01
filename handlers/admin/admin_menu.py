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


settings = get_settings()


async def admin_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user:
        return

    if user.id not in settings.ADMIN_IDS:
        await update.message.reply_text(
            "⛔ Нет доступа"
        )

        return

    await update.message.reply_text(
        "⚙️ Админ панель",
        reply_markup=get_admin_menu(),
    )
