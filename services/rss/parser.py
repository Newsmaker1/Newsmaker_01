import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class RSSParser:
    @staticmethod
    def parse_entry(
        entry: Any,
    ) -> dict[str, Any]:
        title = entry.get("title", "").strip()

        link = entry.get("link", "").strip()

        summary = (
            entry.get("summary", "")
            or entry.get("description", "")
        )

        published_at = RSSParser._parse_date(
            entry
        )

        image_url = RSSParser._extract_image(
            entry,
            summary,
        )

        categories = RSSParser._extract_categories(
            entry
        )

        return {
            "title": title,
            "link": link,
            "summary": summary,
            "published_at": published_at,
            "image_url": image_url,
            "categories": categories,
        }

    @staticmethod
    def _parse_date(
        entry: Any,
    ) -> datetime | None:
        date_fields = [
            "published",
            "updated",
            "created",
        ]

        for field in date_fields:
            value = entry.get(field)

            if not value:
                continue

            try:
                return parsedate_to_datetime(
                    value
                )
            except Exception:
                continue

        return None

    @staticmethod
    def _extract_image(
        entry: Any,
        html: str,
    ) -> str | None:
        media_content = entry.get(
            "media_content"
        )

        if media_content:
            try:
                return media_content[0].get(
                    "url"
                )
            except Exception:
                pass

        media_thumbnail = entry.get(
            "media_thumbnail"
        )

        if media_thumbnail:
            try:
                return media_thumbnail[0].get(
                    "url"
                )
            except Exception:
                pass

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        img = soup.find("img")

        if img:
            return img.get("src")

        return None

    @staticmethod
    def _extract_categories(
        entry: Any,
    ) -> list[str]:
        tags = entry.get("tags", [])

        result = []

        for tag in tags:
            term = tag.get("term")

            if term:
                result.append(term)

        return result
