import logging

from services.html.adapter_registry import (
    AdapterRegistry,
)

from services.rss.fetcher import (
    RSSFetcher,
)


logger = logging.getLogger(__name__)


class HTMLEngine:

    def __init__(
        self,
    ) -> None:

        self.fetcher = RSSFetcher()

    # ==================================================
    # PROCESS SOURCE
    # ==================================================

    async def process_source(
        self,
        source,
    ) -> list[dict]:

        logger.info(
            f"Processing HTML source: "
            f"{source.source_url}"
        )

        # ==============================================
        # GET ADAPTER
        # ==============================================

        adapter = (
            AdapterRegistry.get_adapter(
                source.parser_strategy
            )
        )

        # ==============================================
        # FETCH LIST PAGE
        # ==============================================

        result = await self.fetcher.fetch(
            source.source_url
        )

        if (
            result["status"]
            != "success"
        ):

            logger.warning(
                f"HTML fetch failed: "
                f"{source.source_url}"
            )

            return []

        html = result["content"]

        if not html:

            logger.warning(
                "Empty HTML response"
            )

            return []

        # ==============================================
        # EXTRACT LINKS
        # ==============================================

        try:

            links = (
                await adapter.extract_links(
                    html=html,
                    source_url=(
                        source.source_url
                    ),
                )
            )

        except Exception as exc:

            logger.exception(
                f"Link extraction failed: "
                f"{exc}"
            )

            return []

        if not links:

            logger.warning(
                "No article links found"
            )

            return []

        logger.info(
            f"Extracted "
            f"{len(links)} article links"
        )

        # ==============================================
        # PROCESS ARTICLES
        # ==============================================

        articles = []

        for article_url in links[:20]:

            try:

                article = await (
                    self._process_article(
                        adapter=adapter,
                        article_url=article_url,
                    )
                )

                if article:

                    articles.append(
                        article
                    )

            except Exception as exc:

                logger.exception(
                    f"Article parse failed: "
                    f"{article_url} "
                    f"{exc}"
                )

        logger.info(
            f"Parsed "
            f"{len(articles)} articles"
        )

        return articles

    # ==================================================
    # PROCESS ARTICLE
    # ==================================================

    async def _process_article(
        self,
        adapter,
        article_url: str,
    ) -> dict | None:

        result = await self.fetcher.fetch(
            article_url
        )

        if (
            result["status"]
            != "success"
        ):

            return None

        html = result["content"]

        if not html:

            return None

        article = await adapter.parse_article(
            html=html,
            article_url=article_url,
        )

        if not article:

            return None

        article["source_url"] = (
            article_url
        )

        return article
