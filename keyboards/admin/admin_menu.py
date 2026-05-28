from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.constants.buttons import (
    BACK_BUTTON,
)


# ==================================================
# ADMIN MENU
# ==================================================

def get_admin_menu():

    keyboard = [

        [
            KeyboardButton(
                text="📰 Источники"
            )
        ],

        [
            KeyboardButton(
                text="📦 Пакеты"
            )
        ],

        [
            KeyboardButton(
                text="📬 Дестинейшны"
            )
        ],

        [
            KeyboardButton(
                text="📊 Мониторинг"
            )
        ],

        [
            KeyboardButton(
                text="📨 Рассылка"
            )
        ],

        [
            KeyboardButton(
                text="👥 Пользователи"
            )
        ],

        [
            KeyboardButton(
                text="⚙️ Система"
            )
        ],

        [
            KeyboardButton(
                text=BACK_BUTTON
            )
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )
