import re
import unicodedata

from bs4 import BeautifulSoup


TRACKING_PATTERNS = [
    r"utm_[a-zA-Z0-9_]+=[^&]+",
    r"fbclid=[^&]+",
    r"gclid=[^&]+",
]


class RSSCleaner:
    @staticmethod
    def clean_html(
        html: str,
    ) -> str:
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup(
            [
                "script",
                "style",
                "iframe",
                "noscript",
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" "
        )

        text = unicodedata.normalize(
            "NFKC",
            text
        )

        text = RSSCleaner._remove_tracking(
            text
        )

        text = RSSCleaner._cleanup_spaces(
            text
        )

        return text.strip()

    @staticmethod
    def _remove_tracking(
        text: str,
    ) -> str:
        for pattern in TRACKING_PATTERNS:
            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE,
            )

        return text

    @staticmethod
    def _cleanup_spaces(
        text: str,
    ) -> str:
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text
