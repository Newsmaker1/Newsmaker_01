import asyncio
import logging
import feedparser
import aiohttp
from datetime import datetime, timezone, timedelta

from aiogram import Bot

from database import (
    get_active_feeds,
    get_active_channels,
    is_link_posted,
    save_posted_link,
    cleanup_old_posts
)

logger = logging.getLogger(__name__)

# =========================
# НАСТРОЙКИ
# =========================

CHECK_INTERVAL = 300
POST_DELAY = 10
MAX_POSTS_PER_FEED = 5
NEWS_MAX_AGE = 24


# =========================
# ВРЕМЯ НОВОСТИ
# =========================

def is_fresh(entry):

    if not hasattr(entry, "published_parsed"):
        return True

    published = datetime(
        *entry.published_parsed[:6],
        tzinfo=timezone.utc
    )

    now = datetime.now(timezone.utc)

    age = now - published

    return age < timedelta(
        hours=NEWS_MAX_AGE
    )


# =========================
# HTML
# =========================

async def fetch_html(url):

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:

                return await resp.text()

    except Exception as e:

        logger.error(
            f"HTML fetch error: {e}"
        )

        return None


# =========================
# КАРТИНКА ИЗ HTML
# =========================

def extract_large_image(html):

    if not html:
        return None

    import re

    images = re.findall(
        r'<img[^>]+src="([^">]+)"',
        html
    )

    for img in images:

        img_lower = img.lower()

        if any(x in img_lower for x in [

            "logo",
            "icon",
            "small",
            "banner",
            "avatar",
            "thumb"

        ]):
            continue

        return img

    return None


# =========================
# КАРТИНКА RSS
# =========================

def get_entry_image(entry):

    if "media_content" in entry:

        return entry.media_content[0].get(
            "url"
        )

    if "links" in entry:

        for link in entry.links:

            if link.type.startswith("image"):
                return link.href

    return None


# =========================
# ТЕКСТ
# =========================

def build_caption(title, description, source, link):

    return (

        f"<b>{title}</b>\n\n"

        f"{description}\n\n"

        f"Источник: {source}\n\n"

        f"<a href='{link}'>Читать полностью</a>\n"

        "──────────────"

    )


# =========================
# RSS LOOP
# =========================

async def rss_loop(bot: Bot):

    logger.info("RSS цикл запущен")

    while True:

        try:

            feeds = await get_active_feeds()

            channels = await get_active_channels()

            if not feeds or not channels:

                await asyncio.sleep(
                    CHECK_INTERVAL
                )
                continue

            for feed in feeds:

                feed_id, name, url = feed

                try:

                    parsed = feedparser.parse(url)

                            

                    if not parsed.entries:

                        continue

                    entries = parsed.entries[
                        :MAX_POSTS_PER_FEED
                    ]

                    for entry in entries:

                        link = entry.link

                        title = entry.title

                        description = getattr(
                            entry,
                            "summary",
                            ""
                        )

                        if not is_fresh(entry):
                            continue

                        if await is_link_posted(link):
                            continue

                        image = get_entry_image(
                            entry
                        )

                        if not image:

                            html = await fetch_html(
                                link
                            )

                            image = extract_large_image(
                                html
                            )

                        caption = build_caption(

                            title,
                            description,
                            name,
                            link

                        )

                        for channel in channels:

                            chat_id, thread_id, _ = channel

                            try:

                                if image:

                                    if thread_id:

                                        await bot.send_photo(

                                            chat_id,

                                            photo=image,

                                            caption=caption,

                                            message_thread_id=thread_id

                                        )

                                    else:

                                        await bot.send_photo(

                                            chat_id,

                                            photo=image,

                                            caption=caption

                                        )

                                else:

                                    raise Exception(
                                        "No image"
                                    )

                            except Exception:

                                # fallback если фото не отправилось

                                try:

                                    if thread_id:

                                        await bot.send_message(

                                            chat_id,

                                            caption,

                                            message_thread_id=thread_id

                                        )

                                    else:

                                        await bot.send_message(

                                            chat_id,

                                            caption

                                        )

                                except Exception as e:

                                    logger.error(
                                        f"Send error: {e}"
                                    )

                        await save_posted_link(
                            link,
                            title
                        )

                        await asyncio.sleep(
                            POST_DELAY
                        )

                except Exception as e:

                    logger.error(
                        f"RSS parse error: {url} {e}"
                    )

        except Exception as e:

            logger.error(
                f"RSS error: {e}"
            )

        await asyncio.sleep(
            CHECK_INTERVAL
        )


# =========================
# CLEANUP
# =========================

async def cleanup_loop():

    await asyncio.sleep(300)

    while True:

        try:

            logger.info(
                "[CLEANUP] Запуск очистки"
            )

            deleted = await cleanup_old_posts(
                hours=72
            )

            logger.info(
                f"[CLEANUP DONE] {deleted}"
            )

        except Exception as e:

            logger.error(
                f"[CLEANUP ERROR] {e}"
            )

        await asyncio.sleep(
            43200
        )
