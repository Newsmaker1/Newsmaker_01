import hashlib
import logging

from rapidfuzz import fuzz
from sqlalchemy import select

from config.settings import get_settings
from database.session import AsyncSessionLocal
from models.post import Post


logger = logging.getLogger(__name__)

settings = get_settings()


class DuplicateDetector:
    @staticmethod
    def make_sha256(
        text: str,
    ) -> str:
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    async def is_duplicate_url(
        url_hash: str,
    ) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Post.id).where(
                    Post.url_hash == url_hash
                )
            )

            return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_duplicate_content(
        content_hash: str,
    ) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Post.id).where(
                    Post.content_hash
                    == content_hash
                )
            )

            return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_similar_content(
        text: str,
    ) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    Post.id,
                    Post.translated_content,
                )
                .order_by(
                    Post.created_at.desc()
                )
                .limit(50)
            )

            posts = result.all()

        for _, existing_text in posts:
            if not existing_text:
                continue

            similarity = fuzz.ratio(
                text,
                existing_text,
            )

            if (
                similarity
                >= settings.SIMILARITY_THRESHOLD
            ):
                logger.info(
                    f"Similar content detected: "
                    f"{similarity}%"
                )

                return True

        return False
