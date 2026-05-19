import html
import re


class TelegramFormatter:
    @staticmethod
    def escape_markdown(
        text: str,
    ) -> str:
        escape_chars = r"_*[]()~`>#+-=|{}.!"

        pattern = (
            f"([{re.escape(escape_chars)}])"
        )

        return re.sub(
            pattern,
            r"\\\1",
            text,
        )

    @staticmethod
    def build_post(
        title: str,
        content: str,
        source_url: str,
    ) -> str:
        safe_title = (
            TelegramFormatter
            .escape_markdown(title)
        )

        safe_content = (
            TelegramFormatter
            .escape_markdown(content)
        )

        safe_url = html.escape(source_url)

        text = (
            f"*{safe_title}*\n\n"
            f"{safe_content}\n\n"
            f"[Источник]({safe_url})"
        )

        if len(text) > 4000:
            text = text[:3900] + "..."

        return text
