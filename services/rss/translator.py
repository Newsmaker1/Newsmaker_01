import hashlib
import logging

from deep_translator import (
    GoogleTranslator,
)

from langdetect import (
    detect,
    LangDetectException,
)

from sqlalchemy import (
    select,
)

from database.session import (
    AsyncSessionLocal,
)

from models.translation_cache import (
    TranslationCache,
)


logger = logging.getLogger(__name__)


class TranslatorService:

    def __init__(
        self,
        target_language: str = "ru",
    ) -> None:

        self.target_language = (
            target_language
        )

    # ==================================================
    # TRANSLATE
    # ==================================================

    async def translate(
        self,
        text: str,
    ) -> str:

        # ==============================================
        # EMPTY TEXT
        # ==============================================

        if not text:
            return ""

        text = text.strip()

        if not text:
            return ""

        # ==============================================
        # SHORT TEXT
        # ==============================================

        if len(text) < 3:
            return text

        # ==============================================
        # DETECT LANGUAGE
        # ==============================================

        try:

            detected_language = detect(
                text
            )

        except LangDetectException:

            logger.warning(
                "Language detection failed"
            )

            return text

        # ==============================================
        # SKIP TARGET LANGUAGE
        # ==============================================

        if (
            detected_language
            == self.target_language
        ):

            logger.info(
                "Translation skipped "
                f"({detected_language})"
            )

            return text

        # ==============================================
        # CONTENT HASH
        # ==============================================

        content_hash = (
            self._build_hash(
                text
            )
        )

        # ==============================================
        # CACHE LOOKUP
        # ==============================================

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(TranslationCache)
                .where(
                    TranslationCache.content_hash
                    == content_hash,
                    TranslationCache.target_language
                    == self.target_language,
                )
            )

            cache = (
                result.scalar_one_or_none()
            )

            if cache:

                logger.info(
                    "Translation cache hit"
                )

                return cache.translated_text

        # ==============================================
        # TRANSLATE
        # ==============================================

        try:

            translated_text = (
                GoogleTranslator(
                    source="auto",
                    target=self.target_language,
                ).translate(text)
            )

            if not translated_text:

                return text

        except Exception as exc:

            logger.exception(
                f"Translation failed: "
                f"{exc}"
            )

            return text

        # ==============================================
        # SAVE CACHE
        # ==============================================

        try:

            async with AsyncSessionLocal() as session:

                cache = TranslationCache(
                    content_hash=content_hash,
                    source_language=(
                        detected_language
                    ),
                    target_language=(
                        self.target_language
                    ),
                    original_text=text,
                    translated_text=(
                        translated_text
                    ),
                )

                session.add(cache)

                await session.commit()

        except Exception as exc:

            logger.exception(
                f"Cache save failed: "
                f"{exc}"
            )

        logger.info(
            f"Translated "
            f"{detected_language} "
            f"-> "
            f"{self.target_language}"
        )

        return translated_text

    # ==================================================
    # HASH
    # ==================================================

    @staticmethod
    def _build_hash(
        text: str,
    ) -> str:

        normalized = (
            text.strip()
            .lower()
        )

        return hashlib.sha256(
            normalized.encode(
                "utf-8"
            )
        ).hexdigest()
