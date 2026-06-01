import logging

from telegram import Update

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from states.rss_state import RSS_ADD_STATE

from config.settings import (
    get_settings,
)

from bot.constants.buttons import (
    ADMIN_BUTTON,
)

from handlers.start import (
    start_handler,
)

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
    destination_callback_handler,
    destinations_handler,
)

from handlers.admin.source_health import (
    source_health_handler,
)

from handlers.admin.back import (
    back_handler,
)

from states.pack_state import (
    PACK_ADD_STATE,
)

from states.source_state import (
    RSS_ADD_STATE,
)

from states.destination_state import (
    DESTINATION_ADD_STATE,
)

logger = logging.getLogger(__name__)

settings = get_settings()


# ==================================================
# FSM ROUTER
# ==================================================

async def fsm_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        return

    user_id = user.id

    # ==============================================
    # PACK FSM
    # ==============================================

    if user_id in PACK_ADD_STATE:

        await add_pack_handler(
            update,
            context,
        )

        return

    # ==============================================
    # RSS FSM
    # ==============================================

    if user_id in RSS_ADD_STATE:

        await add_rss_handler(
            update,
            context,
        )

        return

    # ==============================================
    # DESTINATION FSM
    # ==============================================

    if user_id in DESTINATION_ADD_STATE:

        await add_destination_handler(
            update,
            context,
        )

        return


# ==================================================
# CREATE APPLICATION
# ==================================================

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
    # FSM ROUTER
    # ==================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            fsm_router,
        ),
        group=1,
    )

    # ==================================================
    # CALLBACKS
    # ==================================================

    application.add_handler(
        CallbackQueryHandler(
            rss_callback_handler,
            pattern="^rss_",
        ),
        group=2,
    )

    application.add_handler(
        CallbackQueryHandler(
            pack_callback_handler,
            pattern="^pack_",
        ),
        group=2,
    )

    application.add_handler(
        CallbackQueryHandler(
            destination_callback_handler,
            pattern="^destination_",
        ),
        group=2,
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
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📰 Источники$"
            ),
            rss_sources_handler,
        ),
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📦 Пакеты$"
            ),
            source_packs_handler,
        ),
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📬 Дестинейшны$"
            ),
            destinations_handler,
        ),
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^📊 Мониторинг$"
            ),
            source_health_handler,
        ),
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(
                "^⬅️ Назад$"
            ),
            back_handler,
        ),
        group=3,
    )

    logger.info(
        "Telegram application initialized"
    )

    return application
