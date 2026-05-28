from urllib.parse import (
    urljoin,
)

from bs4 import BeautifulSoup

from services.html.base_adapter import (
    BaseHTMLAdapter,
)


class DefaultHTMLAdapter(
    BaseHTMLAdapter
):

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

        for a in soup.find_all("a"):

            href = a.get("href")

            if not href:
                continue

            if href.startswith(
                "javascript:"
            ):
                continue

            full_url = urljoin(
                source_url,
                href,
            )

            if full_url not in links:
                links.append(full_url)

        return links[:100]

    async def parse_article(
        self,
        html: str,
        article_url: str,
    ) -> dict:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ==========================================
        # REMOVE TRASH
        # ==========================================

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "iframe",
                "header",
                "footer",
                "nav",
                "aside",
            ]
        ):
            tag.decompose()

        # ==========================================
        # TITLE
        # ==========================================

        title = ""

        if soup.title:
            title = (
                soup.title.text.strip()
            )

        # ==========================================
        # ARTICLE
        # ==========================================

        article = (
            soup.find("article")
            or soup.body
        )

        paragraphs = []

        if article:

            for p in article.find_all("p"):

                text = p.get_text(
                    " ",
                    strip=True,
                )

                if len(text) > 40:
                    paragraphs.append(
                        text
                    )

        content = "\n\n".join(
            paragraphs[:30]
        )

        # ==========================================
        # IMAGE
        # ==========================================

        image_url = None

        image = soup.find("img")

        if image:

            src = image.get("src")

            if src:

                image_url = urljoin(
                    article_url,
                    src,
                )

        return {
            "title": title,
            "content": content,
            "image_url": image_url,
            "published_at": None,
        }
