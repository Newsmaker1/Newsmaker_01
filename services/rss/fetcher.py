import logging
from typing import Any

import feedparser
import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()


class RSSFetchError(Exception):
    pass


class RSSFetcher:
    def __init__(self) -> None:
        self.timeout = 30

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=15),
        retry=retry_if_exception_type(
            (
                httpx.HTTPError,
                RSSFetchError,
            )
        ),
        reraise=True,
    )
    async def fetch(
        self,
        url: str,
        etag: str | None = None,
        modified: str | None = None,
    ) -> dict[str, Any]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; NewsmakerBot/1.0)"
            )
        }

        if etag:
            headers["If-None-Match"] = etag

        if modified:
            headers["If-Modified-Since"] = modified

        logger.info(f"Fetching RSS: {url}")

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers=headers,
            )

        if response.status_code == 304:
            logger.info(
                f"Feed not modified: {url}"
            )

            return {
                "status": "not_modified",
                "feed": None,
                "etag": etag,
                "modified": modified,
            }

        if response.status_code >= 400:
            raise RSSFetchError(
                f"HTTP {response.status_code}"
            )

        parsed_feed = feedparser.parse(
            response.content
        )

        if parsed_feed.bozo:
            logger.warning(
                f"Bozo feed detected: {url}"
            )

        logger.info(
            f"RSS fetched successfully: {url}"
        )

        return {
            "status": "success",
            "feed": parsed_feed,
            "etag": response.headers.get("ETag"),
            "modified": response.headers.get(
                "Last-Modified"
            ),
        }
