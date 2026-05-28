from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


# ==================================================
# PACKS MENU
# ==================================================

def get_packs_menu():

    keyboard = [

        [

            InlineKeyboardButton(
                text="➕ Создать пакет",
                callback_data="pack_add",
            )

        ],

        [

            InlineKeyboardButton(
                text="📋 Список пакетов",
                callback_data="pack_list",
            )

        ],

    ]

    return InlineKeyboardMarkup(
        keyboard
    )
