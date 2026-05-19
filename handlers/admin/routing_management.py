import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from database.session import (
    AsyncSessionLocal,
)
from models.destination import (
    Destination,
)
from models.routing_rule import (
    RoutingRule,
)
from models.source_pack import (
    SourcePack,
)


logger = logging.getLogger(__name__)


async def routing_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                RoutingRule,
                SourcePack,
                Destination,
            )
            .join(
                SourcePack,
                RoutingRule.pack_id
                == SourcePack.id,
            )
            .join(
                Destination,
                RoutingRule.destination_id
                == Destination.id,
            )
        )

        rows = result.all()

    if not rows:
        text = (
            "🔀 Routing Rules\n\n"
            "Routing rules пока нет."
        )
    else:
        lines = [
            "🔀 Routing Rules\n"
        ]

        for (
            rule,
            pack,
            destination,
        ) in rows:
            lines.append(
                f"ID: {rule.id}\n"
                f"Pack: {pack.name}\n"
                f"Destination: "
                f"{destination.title}\n"
                f"Active: "
                f"{rule.is_active}\n"
            )

        text = "\n".join(lines)

    text += (
        "\n\n"
        "Создать routing:\n"
        "/add_route PACK_ID "
        "DESTINATION_ID"
    )

    await update.message.reply_text(
        text
    )


async def add_route_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        args = context.args

        if len(args) < 2:
            await update.message.reply_text(
                "Использование:\n"
                "/add_route "
                "PACK_ID DESTINATION_ID"
            )

            return

        pack_id = int(args[0])

        destination_id = int(args[1])

        async with AsyncSessionLocal() as session:
            pack = await session.get(
                SourcePack,
                pack_id,
            )

            if not pack:
                await update.message.reply_text(
                    "❌ Pack не найден"
                )

                return

            destination = await session.get(
                Destination,
                destination_id,
            )

            if not destination:
                await update.message.reply_text(
                    "❌ Destination не найден"
                )

                return

            existing = await session.execute(
                select(RoutingRule).where(
                    RoutingRule.pack_id
                    == pack_id,
                    RoutingRule.destination_id
                    == destination_id,
                )
            )

            if existing.scalar_one_or_none():
                await update.message.reply_text(
                    "❌ Routing уже существует"
                )

                return

            rule = RoutingRule(
                user_id=1,
                pack_id=pack_id,
                destination_id=destination_id,
                is_active=True,
            )

            session.add(rule)

            await session.commit()

        await update.message.reply_text(
            "✅ Routing создан"
        )

        logger.info(
            f"Routing created: "
            f"{pack_id} -> "
            f"{destination_id}"
        )

    except Exception as exc:
        logger.exception(exc)

        await update.message.reply_text(
            f"❌ Ошибка:\n{exc}"
        )
