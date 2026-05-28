import time


class HTMLCircuitBreaker:

    FAILURE_THRESHOLD = 5

    RECOVERY_TIMEOUT = 1800

    _failures = {}

    _blocked_until = {}

    # ==================================================
    # IS AVAILABLE
    # ==================================================

    @classmethod
    def is_available(
        cls,
        domain: str,
    ) -> bool:

        blocked_until = (
            cls._blocked_until.get(
                domain
            )
        )

        if not blocked_until:
            return True

        if time.time() >= blocked_until:

            cls._blocked_until.pop(
                domain,
                None,
            )

            cls._failures.pop(
                domain,
                None,
            )

            return True

        return False

    # ==================================================
    # RECORD FAILURE
    # ==================================================

    @classmethod
    def record_failure(
        cls,
        domain: str,
    ) -> None:

        failures = (
            cls._failures.get(
                domain,
                0,
            )
            + 1
        )

        cls._failures[domain] = failures

        if (
            failures
            >= cls.FAILURE_THRESHOLD
        ):

            cls._blocked_until[
                domain
            ] = (
                time.time()
                + cls.RECOVERY_TIMEOUT
            )

    # ==================================================
    # RECORD SUCCESS
    # ==================================================

    @classmethod
    def record_success(
        cls,
        domain: str,
    ) -> None:

        cls._failures.pop(
            domain,
            None,
        )

        cls._blocked_until.pop(
            domain,
            None,
        )
