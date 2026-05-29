import logging

from sqlalchemy import (
    select,
)

from telegram import (
    Update,
)

from telegram.ext import (
    ContextTypes,
)

from database.session import (
    AsyncSessionLocal,
)

from keyboards.admin.admin_menu import (
    get_admin_menu,
)

from models.source_health import (
    SourceHealth,
)

from models.source_pack import (
    PackSource,
)

from bot.constants.buttons import (
    STATISTICS_BUTTON,
)


logger = logging.getLogger(__name__)


# ==================================================
# SOURCE HEALTH DASHBOARD
# ==================================================

async def source_health_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    if (
        update.message.text
        != STATISTICS_BUTTON
    ):
        return

    async with AsyncSessionLocal() as session:

        result = await session.execute(

            select(
                SourceHealth,
                PackSource,
            )
            .join(
                PackSource,
                PackSource.id
                == SourceHealth.source_id,
            )
            .order_by(
                SourceHealth.failure_count.desc()
            )

        )

        rows = result.all()

    # ==============================================
    # EMPTY
    # ==============================================

    if not rows:

        await update.message.reply_text(

            text=(

                "📊 Мониторинг\n\n"

                "Данные отсутствуют."

            ),

            reply_markup=get_admin_menu(),
        )

        return

    # ==============================================
    # BUILD DASHBOARD
    # ==============================================

    lines = [

        "📊 Мониторинг источников\n"

    ]

    total_sources = len(rows)

    active_sources = sum(
        1
        for _, source in rows
        if source.is_active
    )

    lines.append(
        f"Всего источников: "
        f"{total_sources}"
    )

    lines.append(
        f"Активных: "
        f"{active_sources}\n"
    )

    # ==============================================
    # TOP 20
    # ==============================================

    for health, source in rows[:20]:

        total_requests = (

            health.success_count

            + health.failure_count

        )

        success_rate = 0

        if total_requests > 0:

            success_rate = int(

                (
                    health.success_count
                    / total_requests
                )
                * 100

            )

        status = "🟢"

        if not source.is_active:

            status = "🔴"

        elif success_rate < 50:

            status = "🟠"

        source_type = "-"

        try:

            if source.source_type:

                if hasattr(
                    source.source_type,
                    "value"
                ):

                    source_type = (
                        source.source_type.value
                    )

                else:

                    source_type = str(
                        source.source_type
                    )

        except Exception:

            pass

        lines.append(

            f"{status} ID {source.id}\n"

            f"Тип: "
            f"{source_type}\n"

            f"Success: "
            f"{health.success_count}\n"

            f"Failures: "
            f"{health.failure_count}\n"

            f"Rate: "
            f"{success_rate}%\n"

            f"Score: "
            f"{health.average_score}\n"

            f"Active: "
            f"{source.is_active}\n"

            f"URL:\n"
            f"{source.source_url[:80]}\n"

            f"Last Error:\n"
            f"{(health.last_error or '-')[:120]}\n"

        )

    text = "\n".join(lines)

    # ==============================================
    # TELEGRAM LIMIT
    # ==============================================

    if len(text) > 4000:

        text = (
            text[:3900]
            + "\n..."
        )

    await update.message.reply_text(

        text=text,

        reply_markup=get_admin_menu(),

    )
