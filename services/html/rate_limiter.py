import asyncio
import random
import time


class HTMLRateLimiter:

    MIN_DELAY = 1.5

    MAX_DELAY = 4.0

    _last_request_time = 0.0

    # ==================================================
    # WAIT
    # ==================================================

    @classmethod
    async def wait(cls) -> None:

        now = time.time()

        elapsed = (
            now - cls._last_request_time
        )

        random_delay = random.uniform(
            cls.MIN_DELAY,
            cls.MAX_DELAY,
        )

        if elapsed < random_delay:

            await asyncio.sleep(
                random_delay - elapsed
            )

        cls._last_request_time = (
            time.time()
        )
