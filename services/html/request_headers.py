import random


class HTMLRequestHeaders:

    USER_AGENTS = [

        # Chrome Windows
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0.0.0 "
            "Safari/537.36"
        ),

        # Edge
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0.0.0 "
            "Safari/537.36 "
            "Edg/125.0.0.0"
        ),

        # Chrome Android
        (
            "Mozilla/5.0 "
            "(Linux; Android 14) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0.0.0 "
            "Mobile Safari/537.36"
        ),

    ]

    ACCEPT_LANGUAGES = [

        "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",

        "ko,en-US;q=0.9,en;q=0.8",

        "ko-KR,ko;q=0.9",

    ]

    # ==================================================
    # BUILD HEADERS
    # ==================================================

    @classmethod
    def build_headers(
        cls,
    ) -> dict:

        return {

            "User-Agent": random.choice(
                cls.USER_AGENTS
            ),

            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "image/avif,"
                "image/webp,"
                "*/*;q=0.8"
            ),

            "Accept-Language": (
                random.choice(
                    cls.ACCEPT_LANGUAGES
                )
            ),

            "Accept-Encoding": (
                "gzip, deflate, br"
            ),

            "Connection": "keep-alive",

            "Upgrade-Insecure-Requests": "1",

            "Cache-Control": "max-age=0",

        }
