from bs4 import BeautifulSoup


class AdapterDetector:

    # ==================================================
    # DETECT STRATEGY
    # ==================================================

    @classmethod
    def detect_strategy(
        cls,
        html: str,
        source_url: str,
    ) -> str:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        url_lower = (
            source_url.lower()
        )

        html_lower = (
            html.lower()
        )

        # ==============================================
        # EGOV BOARD
        # ==============================================

        egov_patterns = [

            "selectbbsnttlist.do",
            "selectbbsnttview.do",
            "bbsno=",
            "nttno=",
            "egovframework",

        ]

        for pattern in egov_patterns:

            if pattern in url_lower:

                return "egov_board"

            if pattern in html_lower:

                return "egov_board"

        # ==============================================
        # EGOV DOM
        # ==============================================

        egov_selectors = [

            ".board_view",
            ".board_view_con",
            ".bbsView",
            ".view_cont",

        ]

        for selector in egov_selectors:

            if soup.select_one(
                selector
            ):

                return "egov_board"

        # ==============================================
        # DEFAULT
        # ==============================================

        return "default"
