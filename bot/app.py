import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import (
    get_settings,
)

# ==================================================
# BUTTONS
# ==================================================

from bot.constants.buttons import (
    ADMIN_BUTTON,
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
    rss_callback_handler,
    rss_sources_handler,
)

from handlers.admin.pack_management import (
    add_pack_handler,
    pack_callback_handler,
    source_packs_handler,
)

from handlers.admin.destination_management import (
    add_destination_handler,
    destinations_handler,
)

from handlers.admin.statistics import (
    statistics_handler,
)

from handlers.admin.back import (
    back_handler,
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
        ),
        group=0,
    )

    # ==================================================
    # ADMIN MENU
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                f"^{ADMIN_BUTTON}$"
            ),
            admin_menu_handler,
        ),
        group=1,
    )

    # ==================================================
    # RSS SOURCES
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📰 RSS Источники$"
            ),
            rss_sources_handler,
        ),
        group=1,
    )

    application.add_handler(
        CallbackQueryHandler(
            rss_callback_handler,
            pattern="^rss_",
        ),
        group=2,
    )

    # ==================================================
    # SOURCE PACKS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📦 Пакеты источников$"
            ),
            source_packs_handler,
        ),
        group=1,
    )

    application.add_handler(
        CallbackQueryHandler(
            pack_callback_handler,
            pattern="^pack_",
        ),
        group=2,
    )

    # ==================================================
    # DESTINATIONS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📬 Каналы публикации$"
            ),
            destinations_handler,
        ),
        group=1,
    )

    # ==================================================
    # STATISTICS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📊 Статистика$"
            ),
            statistics_handler,
        ),
        group=1,
    )

    # ==================================================
    # BACK
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^⬅️ Назад$"
            ),
            back_handler,
        ),
        group=1,
    )

    # ==================================================
    # FSM HANDLERS
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            add_rss_handler,
        ),
        group=99,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            add_pack_handler,
        ),
        group=99,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            add_destination_handler,
        ),
        group=99,
    )

    # ==================================================
    # LOGGING
    # ==================================================

    logger.info(
        "Telegram application initialized"
    )

    return application
