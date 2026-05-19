import logging

from deep_translator import GoogleTranslator
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()


class TranslationError(Exception):
    pass


class RSSTranslator:
    def __init__(self) -> None:
        self.target_language = (
            settings.DEFAULT_LANGUAGE
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=2,
            min=2,
            max=10,
        ),
        retry=retry_if_exception_type(
            Exception
        ),
        reraise=True,
    )
    async def translate(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        try:
            translated = GoogleTranslator(
                source="auto",
                target=self.target_language,
            ).translate(text)

            if not translated:
                raise TranslationError(
                    "Translation failed"
                )

            return translated

        except Exception as exc:
            logger.error(
                f"Translation error: {exc}"
            )

            raise TranslationError(
                str(exc)
            ) from exc
