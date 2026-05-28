import html
import re
from urllib.parse import urlparse


class TelegramFormatter:

    MAX_TEXT_LENGTH = 4000

    # ==================================================
    # ESCAPE HTML
    # ==================================================

    @staticmethod
    def escape_html(
        text: str,
    ) -> str:

        if not text:
            return ""

        return html.escape(text)

    # ==================================================
    # CLEAN TEXT
    # ==================================================

    @staticmethod
    def clean_text(
        text: str,
    ) -> str:

        if not text:
            return ""

        # ==============================================
        # REMOVE EXTRA SPACES
        # ==============================================

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        # ==============================================
        # REMOVE EMPTY LINES
        # ==============================================

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # ==================================================
    # EXTRACT DOMAIN
    # ==================================================

    @staticmethod
    def extract_domain(
        url: str,
    ) -> str:

        try:

            parsed = urlparse(url)

            domain = (
                parsed.netloc
                .replace("www.", "")
                .strip()
            )

            return domain or "Unknown"

        except Exception:

            return "Unknown"

    # ==================================================
    # GENERATE HASHTAGS
    # ==================================================

    @staticmethod
    def generate_hashtags(
        title: str,
    ) -> str:

        if not title:
            return ""

        words = re.findall(
            r"[A-Za-zА-Яа-я0-9]{4,}",
            title,
        )

        unique_words = []

        for word in words:

            normalized = word.lower()

            if normalized not in unique_words:
                unique_words.append(normalized)

        hashtags = []

        for word in unique_words[:3]:

            cleaned = re.sub(
                r"[^A-Za-zА-Яа-я0-9]",
                "",
                word,
            )

            if cleaned:

                hashtags.append(
                    f"#{cleaned}"
                )

        return " ".join(hashtags)

    # ==================================================
    # TRIM TEXT
    # ==================================================

    @staticmethod
    def trim_text(
        text: str,
        max_length: int,
    ) -> str:

        if len(text) <= max_length:
            return text

        trimmed = text[:max_length]

        last_space = trimmed.rfind(" ")

        if last_space > 0:
            trimmed = trimmed[:last_space]

        return trimmed.strip() + "..."

    # ==================================================
    # BUILD POST
    # ==================================================

    @staticmethod
    def build_post(
        title: str,
        content: str,
        source_url: str,
        attachments: list | None = None,
    ) -> str:

        # ==============================================
        # PREPARE DATA
        # ==============================================

        title = (
            TelegramFormatter.clean_text(
                title
            )
        )

        content = (
            TelegramFormatter.clean_text(
                content
            )
        )

        safe_title = (
            TelegramFormatter.escape_html(
                title
            )
        )

        safe_content = (
            TelegramFormatter.escape_html(
                content
            )
        )

        safe_url = html.escape(
            source_url or ""
        )

        domain = (
            TelegramFormatter.extract_domain(
                source_url
            )
        )

        hashtags = (
            TelegramFormatter.generate_hashtags(
                title
            )
        )

        # ==============================================
        # BUILD MESSAGE
        # ==============================================

        text = ""

        # ==============================================
        # TITLE
        # ==============================================

        if safe_title:

            text += (
                f"📰 <b>{safe_title}</b>\n\n"
            )

        # ==============================================
        # CONTENT
        # ==============================================

        if safe_content:

            content_limit = 2500

            trimmed_content = (
                TelegramFormatter.trim_text(
                    safe_content,
                    content_limit,
                )
            )

            text += (
                f"{trimmed_content}\n\n"
            )

        # ==============================================
        # ATTACHMENTS
        # ==============================================
        
        if attachments:
        
            text += "📎 Документы:\n"
        
            for item in attachments[:5]:
        
                file_name = (
                    TelegramFormatter.escape_html(
                        item.get(
                            "file_name",
                            "document",
                        )
                    )
                )
        
                file_url = html.escape(
                    item.get(
                        "file_url",
                        "",
                    )
                )
        
                text += (
                    f"• "
                    f"<a href=\"{file_url}\">"
                    f"{file_name}"
                    f"</a>\n"
                )
        
            text += "\n"
        
        # ==============================================
        # SOURCE
        # ==============================================

        if safe_url:

            text += (
                f"🔗 "
                f"<a href=\"{safe_url}\">"
                f"Источник"
                f"</a>\n"
            )

        # ==============================================
        # DOMAIN
        # ==============================================

        if domain:

            text += (
                f"🌐 {domain}\n"
            )

        # ==============================================
        # HASHTAGS
        # ==============================================

        if hashtags:

            text += (
                f"\n{hashtags}"
            )

        # ==============================================
        # FINAL TRIM
        # ==============================================

        text = TelegramFormatter.trim_text(
            text,
            TelegramFormatter.MAX_TEXT_LENGTH,
        )

        return text
