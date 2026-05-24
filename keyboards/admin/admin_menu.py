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
                RSS_SOURCES_BUTTON
            )
        ],
        [
            KeyboardButton(
                SOURCE_PACKS_BUTTON
            )
        ],
        [
            KeyboardButton(
                DESTINATIONS_BUTTON
            )
        ],
        [
            KeyboardButton(
                STATISTICS_BUTTON
            )
        ],
        [
            KeyboardButton(
                BACK_BUTTON
            )
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )
