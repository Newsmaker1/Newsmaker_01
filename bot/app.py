import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import (
    get_settings,
)

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

from handlers.admin.destination_management import (
    add_destination_handler,
    destinations_handler,
)


logger = logging.getLogger(__name__)

settings = get_settings()


def create_application() -> Application:
    application = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
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
    # ADMIN MENU
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT,
            admin_menu_handler,
        )
    )

    # ==================================================
    # RSS SOURCES
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT,
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
            filters.TEXT,
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
    # DESTINATIONS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT,
            destinations_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "add_destination",
            add_destination_handler,
        )
    )

    # ==================================================
    # LOGGING
    # ==================================================

    logger.info(
        "Telegram application initialized"
    )

    return application
