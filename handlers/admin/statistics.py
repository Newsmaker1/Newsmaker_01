from telegram import (
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from bot.constants.buttons import (
    STATISTICS_BUTTON,
)

from config.settings import (
    get_settings,
)

settings = get_settings()


async def statistics_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    if (
        update.message.text
        != STATISTICS_BUTTON
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
            "📊 Статистика\n\n"
            "Скоро здесь будет:\n\n"
            "• количество RSS\n"
            "• количество постов\n"
            "• количество доставок\n"
            "• активные каналы\n"
            "• ошибки RSS\n"
            "• uptime\n"
        )
    )
