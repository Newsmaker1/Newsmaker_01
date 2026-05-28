from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from models.source_pack import (
    SourcePack,
)


def build_pack_selector(
    packs: list[SourcePack],
) -> InlineKeyboardMarkup:

    keyboard = []

    for pack in packs:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"📦 "
                        f"{pack.name}"
                    ),
                    callback_data=(
                        f"rss_pack_"
                        f"{pack.id}"
                    ),
                )
            ]
        )

    return InlineKeyboardMarkup(
        keyboard
    )
