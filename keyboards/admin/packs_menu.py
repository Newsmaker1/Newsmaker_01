from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_packs_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить PACK",
                callback_data="pack_add",
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список PACKS",
                callback_data="pack_list",
            )
        ],
    ]

    return InlineKeyboardMarkup(
        keyboard
    )
