import logging

from sqlalchemy import select

from telegram import Update

from telegram.ext import (
    ContextTypes,
)

from bot.constants.buttons import (
    ADMIN_BUTTON,
)

from config.settings import (
    get_settings,
)

from database.session import (
    AsyncSessionLocal,
)

from keyboards.main_menu import (
    get_main_menu_keyboard,
)

from models.user import (
    User,
)


logger = logging.getLogger(__name__)

settings = get_settings()


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    telegram_user = update.effective_user

    if telegram_user is None:
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id
                == telegram_user.id
            )
        )

        user = (
            result.scalar_one_or_none()
        )

        # ==============================================
        # REGISTER NEW USER
        # ==============================================

        if user is None:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=(
                    telegram_user.language_code
                ),
                is_admin=(
                    telegram_user.id
                    in settings.ADMIN_IDS
                ),
            )

            session.add(user)

            await session.commit()

            logger.info(
                f"New user registered: "
                f"{telegram_user.id}"
            )

        # ==============================================
        # UPDATE USER DATA
        # ==============================================

        else:
            user.username = (
                telegram_user.username
            )

            user.first_name = (
                telegram_user.first_name
            )

            user.last_name = (
                telegram_user.last_name
            )

            user.language_code = (
                telegram_user.language_code
            )

            user.is_admin = (
                telegram_user.id
                in settings.ADMIN_IDS
            )

            await session.commit()

    # ==============================================
    # WELCOME MESSAGE
    # ==============================================

    welcome_text = (
        "📰 Добро пожаловать "
        "в систему публикации новостей.\n\n"
        "Используйте меню ниже "
        "для навигации."
    )

    # ==============================================
    # ADMIN INFO
    # ==============================================

    if (
        telegram_user.id
        in settings.ADMIN_IDS
    ):
        welcome_text += (
            f"\n\n"
            f"Доступна панель "
            f"{ADMIN_BUTTON}"
        )

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=(
            get_main_menu_keyboard()
        ),
    )
