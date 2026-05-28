import logging

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


logger = logging.getLogger(__name__)

settings = get_settings()


# ==================================================
# ADMIN MENU
# ==================================================

async def admin_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    if (
        update.message.text
        != ADMIN_BUTTON
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
            f"Unauthorized admin access: "
            f"{user.id}"
        )

        await update.message.reply_text(
            text="⛔ Нет доступа",
        )

        return

    # ==============================================
    # OPEN ADMIN PANEL
    # ==============================================

    logger.info(
        f"Admin panel opened: "
        f"{user.id}"
    )

    await update.message.reply_text(

        text=(

            "🛠 Панель администратора\n\n"

            "Выберите раздел:"

        ),

        reply_markup=get_admin_menu(),
    )
