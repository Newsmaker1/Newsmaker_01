from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_routing_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить routing",
                callback_data="routing_add",
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Routing list",
                callback_data="routing_list",
            )
        ],
    ]

    return InlineKeyboardMarkup(
        keyboard
    )
