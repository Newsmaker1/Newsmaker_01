from abc import (
    ABC,
    abstractmethod,
)


class BaseHTMLAdapter(ABC):

    @abstractmethod
    async def extract_links(
        self,
        html: str,
        source_url: str,
    ) -> list[str]:
        pass

    @abstractmethod
    async def parse_article(
        self,
        html: str,
        article_url: str,
    ) -> dict:
        pass
