from datetime import (
    datetime,
    timedelta,
)


class HTMLNewsFilter:

    MAX_NEWS_AGE_HOURS = 72

    # ==================================================
    # IS OLD NEWS
    # ==================================================

    @classmethod
    def is_old_news(
        cls,
        published_at,
    ) -> bool:

        if not published_at:
            return False

        now = datetime.utcnow()

        max_age = timedelta(
            hours=cls.MAX_NEWS_AGE_HOURS
        )

        return (
            now - published_at
        ) > max_age
