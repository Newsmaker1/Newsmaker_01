from telegram import (
    Update,
)

from telegram.ext import (
    ContextTypes,
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
        text="🏠 Главное меню"
    )
