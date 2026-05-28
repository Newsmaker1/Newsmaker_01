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


class SourceQuarantineService:

    FAILURE_THRESHOLD = 20

    MIN_SUCCESS_RATE = 0.25

    # ==================================================
    # CHECK SOURCE
    # ==================================================

    @classmethod
    async def evaluate_source(
        cls,
        source_id: int,
    ) -> bool:

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
                return False

            total = (
                health.success_count
                + health.failure_count
            )

            if total <= 0:
                return False

            success_rate = (
                health.success_count
                / total
            )

            should_disable = False

            # ==========================================
            # FAILURE COUNT
            # ==========================================

            if (
                health.failure_count
                >= cls.FAILURE_THRESHOLD
            ):

                should_disable = True

            # ==========================================
            # SUCCESS RATE
            # ==========================================

            if (
                success_rate
                < cls.MIN_SUCCESS_RATE
                and total >= 10
            ):

                should_disable = True

            # ==========================================
            # DISABLE SOURCE
            # ==========================================

            if should_disable:

                source_result = (
                    await session.execute(
                        select(PackSource).where(
                            PackSource.id
                            == source_id
                        )
                    )
                )

                source = (
                    source_result
                    .scalars()
                    .first()
                )

                if source:

                    source.is_active = False

                    await session.commit()

                    return True

            return False
