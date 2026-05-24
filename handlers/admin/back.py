from telegram import (
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from keyboards.main_menu import (
    get_main_menu,
)

from bot.constants.buttons import (
    BACK_BUTTON,
)


async def back_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    if (
        update.message.text
        != BACK_BUTTON
    ):
        return

    await update.message.reply_text(
        text="🏠 Главное меню",
        reply_markup=get_main_menu(),
    )
