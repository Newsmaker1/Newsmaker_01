from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton("⭐ Подписка")
        ],
        [
            KeyboardButton("📰 Источники"),
            KeyboardButton("📬 Публикации")
        ],
        [
            KeyboardButton("💬 Поддержка"),
            KeyboardButton("⚙️ Настройки")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
