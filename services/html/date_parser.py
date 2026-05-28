import re

from datetime import (
    datetime,
)


class HTMLDateParser:

    DATE_PATTERNS = [

        # 2026-05-28
        r"\d{4}-\d{2}-\d{2}",

        # 2026.05.28
        r"\d{4}\.\d{2}\.\d{2}",

        # 2026/05/28
        r"\d{4}/\d{2}/\d{2}",

        # 2026년 05월 28일
        r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일",

    ]

    # ==================================================
    # PARSE DATE
    # ==================================================

    @classmethod
    def parse_date(
        cls,
        text: str,
    ) -> datetime | None:

        if not text:
            return None

        for pattern in cls.DATE_PATTERNS:

            match = re.search(
                pattern,
                text,
            )

            if not match:
                continue

            value = match.group(0)

            try:

                # ======================================
                # YYYY-MM-DD
                # ======================================

                if "-" in value:

                    return datetime.strptime(
                        value,
                        "%Y-%m-%d",
                    )

                # ======================================
                # YYYY.MM.DD
                # ======================================

                if "." in value:

                    return datetime.strptime(
                        value,
                        "%Y.%m.%d",
                    )

                # ======================================
                # YYYY/MM/DD
                # ======================================

                if "/" in value:

                    return datetime.strptime(
                        value,
                        "%Y/%m/%d",
                    )

                # ======================================
                # KOREAN
                # ======================================

                if "년" in value:

                    normalized = (
                        value
                        .replace("년", "-")
                        .replace("월", "-")
                        .replace("일", "")
                        .replace(" ", "")
                    )

                    return datetime.strptime(
                        normalized,
                        "%Y-%m-%d",
                    )

            except Exception:

                continue

        return None
