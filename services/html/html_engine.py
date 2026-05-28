import logging

from services.html.adapter_detector import (
    AdapterDetector,
)

from services.html.adapter_registry import (
    AdapterRegistry,
)

from services.html.validator import (
    HTMLValidator,
)

from services.rss.fetcher import (
    RSSFetcher,
)


from services.html.rate_limiter import (
    HTMLRateLimiter,
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
        # FETCH LIST PAGE
        # ==============================================

        await HTMLRateLimiter.wait(
            source.source_url
        )
        
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

        html = result.get("content")

        if not html:

            logger.warning(
                "Empty HTML response"
            )

            return []

        # ==============================================
        # DETECT STRATEGY
        # ==============================================

        strategy = (
            source.parser_strategy
        )

        if (
            not strategy
            or strategy == "auto"
        ):

            detected_strategy = (
                AdapterDetector.detect_strategy(
                    html=html,
                    source_url=(
                        source.source_url
                    ),
                )
            )

            logger.info(
                f"Detected adapter strategy: "
                f"{detected_strategy}"
            )

            strategy = detected_strategy

        # ==============================================
        # GET ADAPTER
        # ==============================================

        adapter = (
            AdapterRegistry.get_adapter(
                strategy
            )
        )

        logger.info(
            f"Using adapter: "
            f"{adapter.__class__.__name__}"
        )

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

        await HTMLRateLimiter.wait(
            article_url
        )
        
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

        html = result.get("content")

        if not html:

            logger.warning(
                f"Empty article HTML: "
                f"{article_url}"
            )

            return None

        # ==============================================
        # FALLBACK ADAPTERS
        # ==============================================

        strategy = getattr(
            adapter,
            "strategy",
            "default",
        )

        fallback_adapters = (
            AdapterRegistry
            .get_fallback_adapters(
                strategy
            )
        )

        best_article = None

        best_score = 0

        for current_adapter in fallback_adapters:

            try:

                article = await (
                    current_adapter.parse_article(
                        html=html,
                        article_url=article_url,
                    )
                )

                if not article:
                    continue

                is_valid, score = (
                    HTMLValidator.validate_article(
                        article
                    )
                )

                logger.info(
                    f"Adapter "
                    f"{current_adapter.__class__.__name__} "
                    f"score={score}"
                )

                if score > best_score:

                    best_score = score

                    best_article = article

                if is_valid:

                    article["source_url"] = (
                        article_url
                    )

                    article[
                        "validation_score"
                    ] = score

                    return article

            except Exception as exc:

                logger.exception(
                    f"Adapter failed: "
                    f"{exc}"
                )

        # ==============================================
        # BEST FALLBACK
        # ==============================================

        if best_article:

            logger.warning(
                f"Using low-score fallback "
                f"article score={best_score}"
            )

            best_article["source_url"] = (
                article_url
            )

            best_article[
                "validation_score"
            ] = best_score

            return best_article

        logger.warning(
            f"All adapters failed: "
            f"{article_url}"
        )

        return None
