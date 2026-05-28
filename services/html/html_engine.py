import logging

from services.html.adapter_registry import (
    AdapterRegistry,
)

from services.rss.fetcher import (
    RSSFetcher,
)

from services.html.validator import (
    HTMLValidator,
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
    
            logger.warning(
                f"Article fetch failed: "
                f"{article_url}"
            )
    
            return None
    
        html = result["content"]
    
        if not html:
    
            logger.warning(
                f"Empty article HTML: "
                f"{article_url}"
            )
    
            return None
    
        # ==============================================
        # PARSE ARTICLE
        # ==============================================
    
        article = await adapter.parse_article(
            html=html,
            article_url=article_url,
        )
    
        if not article:
    
            logger.warning(
                f"Article parsing failed: "
                f"{article_url}"
            )
    
            return None
    
        # ==============================================
        # VALIDATE
        # ==============================================
    
        is_valid, score = (
            HTMLValidator.validate_article(
                article
            )
        )
    
        logger.info(
            f"Article validation "
            f"score={score} "
            f"url={article_url}"
        )
    
        if not is_valid:
    
            logger.warning(
                f"Low quality article skipped: "
                f"{article_url}"
            )
    
            return None
    
        # ==============================================
        # SOURCE URL
        # ==============================================
    
        article["source_url"] = (
            article_url
        )
    
        article["validation_score"] = (
            score
        )
    
        return article
