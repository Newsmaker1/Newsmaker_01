from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_destination_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить канал",
                callback_data="destination_add",
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список каналов",
                callback_data="destination_list",
            )
        ],
    ]

    return InlineKeyboardMarkup(
        keyboard
    )
