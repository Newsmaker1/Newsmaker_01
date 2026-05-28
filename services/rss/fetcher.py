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

from config.settings import (
    get_settings,
)

from services.html.request_headers import (
    HTMLRequestHeaders,
)


logger = logging.getLogger(__name__)

settings = get_settings()


class RSSFetchError(Exception):
    pass


class RSSFetcher:

    def __init__(
        self,
    ) -> None:

        self.timeout = 30

    # ==================================================
    # FETCH
    # ==================================================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=2,
            min=2,
            max=15,
        ),
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

        # ==============================================
        # BROWSER HEADERS
        # ==============================================

        headers = (
            HTMLRequestHeaders.build_headers()
        )

        # ==============================================
        # CACHE HEADERS
        # ==============================================

        if etag:

            headers["If-None-Match"] = (
                etag
            )

        if modified:

            headers[
                "If-Modified-Since"
            ] = modified

        logger.info(
            f"Fetching URL: {url}"
        )

        # ==============================================
        # REQUEST
        # ==============================================

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            http2=True,
        ) as client:

            response = await client.get(
                url,
                headers=headers,
            )

        # ==============================================
        # NOT MODIFIED
        # ==============================================

        if response.status_code == 304:

            logger.info(
                f"Content not modified: "
                f"{url}"
            )

            return {

                "status": "not_modified",

                "feed": None,

                "content": None,

                "etag": etag,

                "modified": modified,

            }

        # ==============================================
        # HTTP ERROR
        # ==============================================

        if response.status_code >= 400:

            raise RSSFetchError(
                f"HTTP {response.status_code}"
            )

        # ==============================================
        # CONTENT
        # ==============================================

        content = response.text

        # ==============================================
        # RSS PARSE
        # ==============================================

        parsed_feed = feedparser.parse(
            response.content
        )

        if parsed_feed.bozo:

            logger.warning(
                f"Bozo feed detected: "
                f"{url}"
            )

        logger.info(
            f"Fetch successful: {url}"
        )

        # ==============================================
        # RESULT
        # ==============================================

        return {

            "status": "success",

            "feed": parsed_feed,

            "content": content,

            "etag": response.headers.get(
                "ETag"
            ),

            "modified": response.headers.get(
                "Last-Modified"
            ),

            "headers": dict(
                response.headers
            ),

            "final_url": str(
                response.url
            ),
        }
