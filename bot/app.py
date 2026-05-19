import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import get_settings

# ==================================================
# USER HANDLERS
# ==================================================

from handlers.start import (
    start_handler,
)

# ==================================================
# ADMIN HANDLERS
# ==================================================

from handlers.admin.admin_menu import (
    admin_menu_handler,
)

from handlers.admin.source_management import (
    add_rss_handler,
    rss_sources_handler,
)

from handlers.admin.pack_management import (
    add_pack_handler,
    source_packs_handler,
)


logger = logging.getLogger(__name__)

settings = get_settings()


def create_application() -> Application:
    application = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .build()
    )

    # ==================================================
    # START
    # ==================================================

    application.add_handler(
        CommandHandler(
            "start",
            start_handler,
        )
    )

    # ==================================================
    # ADMIN PANEL
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Regex(
                "^⚙️ Админ$"
            ),
            admin_menu_handler,
        )
    )

    # ==================================================
    # RSS SOURCES
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Regex(
                "^📰 RSS Источники$"
            ),
            rss_sources_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "add_rss",
            add_rss_handler,
        )
    )

    # ==================================================
    # SOURCE PACKS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Regex(
                "^📦 Source Packs$"
            ),
            source_packs_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "add_pack",
            add_pack_handler,
        )
    )

    # ==================================================
    # LOGGING
    # ==================================================

    logger.info(
        "Telegram application initialized"
    )

    return application
