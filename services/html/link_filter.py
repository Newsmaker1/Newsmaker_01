class HTMLLinkFilter:

    BLOCKED_PATTERNS = [

        "javascript:",
        "login",
        "logout",
        "signup",
        "register",
        "download",
        "filedown",
        "attach",
        ".pdf",
        ".hwp",
        ".doc",
        ".xls",
        "#",
        "mailto:",

    ]

    ALLOWED_PATTERNS = [

        "bbs",
        "board",
        "view",
        "article",
        "notice",
        "ntt",
        "content",

    ]

    # ==================================================
    # VALIDATE LINK
    # ==================================================

    @classmethod
    def is_valid_link(
        cls,
        url: str,
    ) -> bool:

        if not url:
            return False

        url_lower = url.lower()

        # ==============================================
        # BLOCKED
        # ==============================================

        for pattern in cls.BLOCKED_PATTERNS:

            if pattern in url_lower:
                return False

        # ==============================================
        # ALLOWED
        # ==============================================

        for pattern in cls.ALLOWED_PATTERNS:

            if pattern in url_lower:
                return True

        return False
