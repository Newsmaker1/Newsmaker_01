from urllib.parse import (
    urljoin,
)

from bs4 import BeautifulSoup


class HTMLAttachmentExtractor:

    EXTENSIONS = [

        ".pdf",
        ".hwp",
        ".hwpx",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",

    ]

    # ==================================================
    # EXTRACT ATTACHMENTS
    # ==================================================

    @classmethod
    def extract(
        cls,
        html: str,
        article_url: str,
    ) -> list[dict]:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        attachments = []

        for a in soup.find_all("a"):

            href = a.get("href")

            if not href:
                continue

            href_lower = href.lower()

            matched = False

            for ext in cls.EXTENSIONS:

                if ext in href_lower:

                    matched = True

                    break

            if not matched:
                continue

            full_url = urljoin(
                article_url,
                href,
            )

            file_name = (
                a.get_text(
                    " ",
                    strip=True,
                )
                or href.split("/")[-1]
            )

            file_type = None

            for ext in cls.EXTENSIONS:

                if ext in href_lower:

                    file_type = (
                        ext.replace(".", "")
                    )

                    break

            attachments.append({

                "file_name": file_name,

                "file_url": full_url,

                "file_type": file_type,

            })

        return attachments
