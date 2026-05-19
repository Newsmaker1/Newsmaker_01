from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.constants.buttons import (
    ADMIN_BUTTON,
    PUBLICATIONS_BUTTON,
    SETTINGS_BUTTON,
    SOURCES_BUTTON,
    SUBSCRIPTION_BUTTON,
    SUPPORT_BUTTON,
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(
                SUBSCRIPTION_BUTTON
            )
        ],
        [
            KeyboardButton(
                SOURCES_BUTTON
            ),
            KeyboardButton(
                PUBLICATIONS_BUTTON
            ),
        ],
        [
            KeyboardButton(
                ADMIN_BUTTON
            )
        ],
        [
            KeyboardButton(
                SUPPORT_BUTTON
            ),
            KeyboardButton(
                SETTINGS_BUTTON
            ),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )
