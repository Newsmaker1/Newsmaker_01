from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy import select

from database.session import (
    AsyncSessionLocal,
)

from models.source_health import (
    SourceHealth,
)

from models.source_pack import (
    PackSource,
)


class SourceReactivationService:

    REACTIVATION_HOURS = 24

    # ==================================================
    # REACTIVATE SOURCES
    # ==================================================

    @classmethod
    async def reactivate_sources(
        cls,
    ) -> int:

        restored = 0

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(
                    PackSource,
                    SourceHealth,
                )
                .join(
                    SourceHealth,
                    PackSource.id
                    == SourceHealth.source_id,
                )
                .where(
                    PackSource.is_active.is_(
                        False
                    )
                )
            )

            rows = result.all()

            now = datetime.utcnow()

            for source, health in rows:

                if not (
                    health.last_failure_at
                ):
                    continue

                delta = (
                    now
                    - health.last_failure_at
                )

                if delta < timedelta(
                    hours=(
                        cls.REACTIVATION_HOURS
                    )
                ):
                    continue

                # ======================================
                # REACTIVATE
                # ======================================

                source.is_active = True

                restored += 1

            await session.commit()

        return restored
