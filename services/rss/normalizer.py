import re
import unicodedata


class RSSNormalizer:
    @staticmethod
    def normalize_text(
        text: str,
    ) -> str:
        if not text:
            return ""

        text = unicodedata.normalize(
            "NFKC",
            text
        )

        text = RSSNormalizer._normalize_quotes(
            text
        )

        text = RSSNormalizer._normalize_dashes(
            text
        )

        text = RSSNormalizer._cleanup_whitespace(
            text
        )

        text = RSSNormalizer._cleanup_punctuation(
            text
        )

        return text.strip()

    @staticmethod
    def _normalize_quotes(
        text: str,
    ) -> str:
        replacements = {
            "“": '"',
            "”": '"',
            "„": '"',
            "«": '"',
            "»": '"',
            "‘": "'",
            "’": "'",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def _normalize_dashes(
        text: str,
    ) -> str:
        replacements = {
            "—": "-",
            "–": "-",
            "−": "-",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def _cleanup_whitespace(
        text: str,
    ) -> str:
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    @staticmethod
    def _cleanup_punctuation(
        text: str,
    ) -> str:
        text = re.sub(
            r"\.{2,}",
            ".",
            text
        )

        text = re.sub(
            r"\!{2,}",
            "!",
            text
        )

        text = re.sub(
            r"\?{2,}",
            "?",
            text
        )

        return text
