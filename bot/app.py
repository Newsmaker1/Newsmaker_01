import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.admin.admin_menu import (
    admin_menu_handler,
)

from config.settings import get_settings
from handlers.start import start_handler


logger = logging.getLogger(__name__)

settings = get_settings()


def create_application() -> Application:
    application = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT("⚙️ Админ"),
            admin_menu_handler,
        )
    )
    
    logger.info("Telegram application initialized")

    return application
