from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_admin_menu():
    keyboard = [
        [
            KeyboardButton(
                "📰 RSS Источники"
            )
        ],
        [
            KeyboardButton(
                "📦 Source Packs"
            )
        ],
        [
            KeyboardButton(
                "📬 Destinations"
            )
        ],
        [
            KeyboardButton(
                "🔀 Routing"
            )
        ],
        [
            KeyboardButton(
                "📊 Статистика"
            )
        ],
        [
            KeyboardButton(
                "⬅️ Назад"
            )
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
