import re


class HTMLValidator:

    # ==================================================
    # VALIDATE ARTICLE
    # ==================================================

    @staticmethod
    def validate_article(
        article: dict,
    ) -> tuple[bool, int]:

        score = 0

        title = (
            article.get(
                "title",
                "",
            )
            .strip()
        )

        content = (
            article.get(
                "content",
                "",
            )
            .strip()
        )

        # ==============================================
        # TITLE
        # ==============================================

        if len(title) >= 10:

            score += 20

        # ==============================================
        # CONTENT LENGTH
        # ==============================================

        if len(content) >= 300:

            score += 30

        elif len(content) >= 150:

            score += 15

        # ==============================================
        # PARAGRAPHS
        # ==============================================

        paragraphs = content.count(
            "\n"
        )

        if paragraphs >= 3:

            score += 15

        # ==============================================
        # SENTENCES
        # ==============================================

        sentences = re.split(
            r"[.!?。\n]",
            content,
        )

        if len(sentences) >= 5:

            score += 15

        # ==============================================
        # GARBAGE FILTER
        # ==============================================

        garbage_patterns = [

            "로그인",
            "회원가입",
            "목록",
            "이전글",
            "다음글",
            "저작권",
            "COPYRIGHT",
            "관리자",
            "본문 바로가기",

        ]

        garbage_hits = 0

        lower_content = (
            content.lower()
        )

        for pattern in garbage_patterns:

            if (
                pattern.lower()
                in lower_content
            ):

                garbage_hits += 1

        if garbage_hits == 0:

            score += 20

        elif garbage_hits >= 4:

            score -= 20

        # ==============================================
        # IMAGE
        # ==============================================

        if article.get("image_url"):

            score += 5

        # ==============================================
        # RESULT
        # ==============================================

        return score >= 50, score
