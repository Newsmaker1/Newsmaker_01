from datetime import datetime

from sqlalchemy import select

from database.session import (
    AsyncSessionLocal,
)

from models.source_health import (
    SourceHealth,
)

from services.html.source_quarantine import (
    SourceQuarantineService,
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

            # ==========================================
            # CREATE HEALTH RECORD
            # ==========================================

            if not health:

                health = SourceHealth(
                    source_id=source_id
                )

                session.add(health)

            # ==========================================
            # SUCCESS METRICS
            # ==========================================

            health.last_success_at = (
                datetime.utcnow()
            )

            health.success_count += 1

            health.last_score = score

            # ==========================================
            # AVERAGE SCORE
            # ==========================================

            total_score = (
                health.average_score
                * (
                    health.success_count
                    - 1
                )
            ) + score

            health.average_score = int(
                total_score
                / health.success_count
            )

            # ==========================================
            # COMMIT
            # ==========================================

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

            # ==========================================
            # CREATE HEALTH RECORD
            # ==========================================

            if not health:

                health = SourceHealth(
                    source_id=source_id
                )

                session.add(health)

            # ==========================================
            # FAILURE METRICS
            # ==========================================

            health.last_failure_at = (
                datetime.utcnow()
            )

            health.failure_count += 1

            health.last_error = (
                error[:1000]
            )

            # ==========================================
            # COMMIT
            # ==========================================

            await session.commit()

        # ==============================================
        # AUTO QUARANTINE
        # ==============================================

        await (
            SourceQuarantineService
            .evaluate_source(
                source_id
            )
        )
