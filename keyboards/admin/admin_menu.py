from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.constants.buttons import (
    BACK_BUTTON,
    DESTINATIONS_BUTTON,
    RSS_SOURCES_BUTTON,
    SOURCE_PACKS_BUTTON,
    STATISTICS_BUTTON,
)


def get_admin_menu():

    keyboard = [
        [
            KeyboardButton(
                text="📰 RSS Источники"
            )
        ],
        [
            KeyboardButton(
                text="📦 Пакеты источников"
            )
        ],
        [
            KeyboardButton(
                text="📬 Каналы публикации"
            )
        ],
        [
            KeyboardButton(
                text="📊 Статистика"
            )
        ],
        [
            KeyboardButton(
                text="⬅️ Назад"
            )
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
    )
