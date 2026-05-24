from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_rss_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить RSS",
                callback_data="rss_add",
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список RSS",
                callback_data="rss_list",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data="rss_refresh",
            )
        ],
    ]

    return InlineKeyboardMarkup(
        keyboard
    )
