from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


# ==================================================
# RSS MENU
# ==================================================

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

    ]

    return InlineKeyboardMarkup(
        keyboard
    )
