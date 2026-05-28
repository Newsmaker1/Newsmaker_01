import asyncio
import random
import time

from urllib.parse import (
    urlparse,
)


class HTMLRateLimiter:

    DEFAULT_MIN_DELAY = 1.5

    DEFAULT_MAX_DELAY = 4.0

    DOMAIN_DELAYS = {

        # ==========================================
        # GOV / MUNICIPAL
        # ==========================================

        "go.kr": (3.0, 7.0),

        "or.kr": (2.5, 6.0),

        "gv.kr": (2.5, 6.0),

    }

    _last_request_times = {}

    # ==================================================
    # GET DOMAIN DELAY
    # ==================================================

    @classmethod
    def get_domain_delay(
        cls,
        domain: str,
    ) -> tuple[float, float]:

        domain = domain.lower()

        for key, value in (
            cls.DOMAIN_DELAYS.items()
        ):

            if domain.endswith(key):

                return value

        return (
            cls.DEFAULT_MIN_DELAY,
            cls.DEFAULT_MAX_DELAY,
        )

    # ==================================================
    # WAIT
    # ==================================================

    @classmethod
    async def wait(
        cls,
        url: str,
    ) -> None:

        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        now = time.time()

        min_delay, max_delay = (
            cls.get_domain_delay(
                domain
            )
        )

        random_delay = random.uniform(
            min_delay,
            max_delay,
        )

        last_request = (
            cls._last_request_times.get(
                domain,
                0.0,
            )
        )

        elapsed = now - last_request

        if elapsed < random_delay:

            await asyncio.sleep(
                random_delay - elapsed
            )

        cls._last_request_times[
            domain
        ] = time.time()
