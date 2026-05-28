from datetime import datetime

from sqlalchemy import select

from database.session import (
    AsyncSessionLocal,
)

from models.source_health import (
    SourceHealth,
)


class SourceHealthService:

    # ==================================================
    # RECORD SUCCESS
    # ==================================================

    @classmethod
    async def record_success(
        cls,
        source_id: int,
        score: int = 0,
    ) -> None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(SourceHealth).where(
                    SourceHealth.source_id
                    == source_id
                )
            )

            health = (
                result.scalars().first()
            )

            if not health:

                health = SourceHealth(
                    source_id=source_id
                )

                session.add(health)

            health.last_success_at = (
                datetime.utcnow()
            )

            health.success_count += 1

            health.last_score = score

            total = (
                health.average_score
                * (
                    health.success_count
                    - 1
                )
            ) + score

            health.average_score = int(
                total / health.success_count
            )

            await session.commit()

    # ==================================================
    # RECORD FAILURE
    # ==================================================

    @classmethod
    async def record_failure(
        cls,
        source_id: int,
        error: str,
    ) -> None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(SourceHealth).where(
                    SourceHealth.source_id
                    == source_id
                )
            )

            health = (
                result.scalars().first()
            )

            if not health:

                health = SourceHealth(
                    source_id=source_id
                )

                session.add(health)

            health.last_failure_at = (
                datetime.utcnow()
            )

            health.failure_count += 1

            health.last_error = error[:1000]

            await session.commit()
