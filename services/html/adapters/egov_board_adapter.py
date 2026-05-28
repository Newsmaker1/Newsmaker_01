from urllib.parse import (
    urljoin,
)

from bs4 import BeautifulSoup

from services.html.base_adapter import (
    BaseHTMLAdapter,
)

from services.html.date_parser import (
    HTMLDateParser,
)


class EGovBoardAdapter(
    BaseHTMLAdapter
):

    strategy = "egov_board"

    # ==================================================
    # EXTRACT LINKS
    # ==================================================

    async def extract_links(
        self,
        html: str,
        source_url: str,
    ) -> list[str]:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        links = []

        # ==============================================
        # EGOV BOARD LINKS
        # ==============================================

        for a in soup.find_all("a"):

            href = a.get("href")

            if not href:
                continue

            href_lower = href.lower()

            if (
                "selectbbsnttview.do"
                not in href_lower
                and "bbsno="
                not in href_lower
            ):
                continue

            full_url = urljoin(
                source_url,
                href,
            )

            if full_url not in links:

                links.append(
                    full_url
                )

        return links[:50]

    # ==================================================
    # PARSE ARTICLE
    # ==================================================

    async def parse_article(
        self,
        html: str,
        article_url: str,
    ) -> dict:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ==============================================
        # REMOVE TRASH
        # ==============================================

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "iframe",
            ]
        ):
            tag.decompose()

        # ==============================================
        # TITLE
        # ==============================================

        title = ""

        title_selectors = [

            ".board_view_title",
            ".view_tit",
            ".bbsViewTitle",
            ".title",

        ]

        for selector in title_selectors:

            node = soup.select_one(
                selector
            )

            if node:

                title = (
                    node.get_text(
                        " ",
                        strip=True,
                    )
                )

                if title:
                    break

        # ==============================================
        # CONTENT
        # ==============================================

        content = ""

        content_selectors = [

            ".board_view_con",
            ".view_cont",
            ".bbsView",
            ".content",
            "#contents",

        ]

        for selector in content_selectors:

            node = soup.select_one(
                selector
            )

            if not node:
                continue

            paragraphs = []

            for p in node.find_all(
                [
                    "p",
                    "div",
                    "span",
                ]
            ):

                text = p.get_text(
                    " ",
                    strip=True,
                )

                if len(text) >= 20:

                    paragraphs.append(
                        text
                    )

            content = "\n\n".join(
                paragraphs
            )

            if len(content) >= 100:
                break

        # ==============================================
        # IMAGE
        # ==============================================

        image_url = None

        image = soup.find("img")

        if image:

            src = image.get("src")

            if src:

                image_url = urljoin(
                    article_url,
                    src,
                )

        # ==============================================
        # DATE
        # ==============================================

        published_at = None

        possible_date_nodes = soup.find_all(
            text=True
        )

        for text in possible_date_nodes:

            parsed_date = (
                HTMLDateParser.parse_date(
                    str(text)
                )
            )

            if parsed_date:

                published_at = (
                    parsed_date
                )

                break

        return {

            "title": title,

            "content": content,

            "image_url": image_url,

            "published_at": published_at,

        }
