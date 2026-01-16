import asyncio
import logging
from enum import StrEnum

import aiohttp
from pydantic import HttpUrl

from src.filters import filter_items
from src.models import Rss
from src.models.rss import Guid, Item
from src.parser import parse_tldr_page

logger = logging.getLogger(__name__)

TLDR_BASE_URL = "https://tldr.tech/api/rss"


class Feed(StrEnum):
    TECH = "Tech"
    AI = "AI"
    DEVOPS = "DevOps"
    DATA = "Data"

    @property
    def url_path(self) -> str:
        return self.value.lower()


feeds: dict[Feed, Rss] = {}


async def fetch(session: aiohttp.ClientSession, url: str) -> bytes:
    async with session.get(url) as response:
        return await response.read()


async def expand_digest_item(
    session: aiohttp.ClientSession, item: Item, feed: Feed
) -> list[Item]:
    """Fetch a digest page and expand it into individual article items."""
    try:
        content = await fetch(session, str(item.link))
        articles = parse_tldr_page(content)

        expanded_items: list[Item] = []
        for article in articles:
            new_item = Item(
                title=f"[{feed.value}] {article.title}",
                link=HttpUrl(article.link),
                guid=Guid(is_perma_link=True, value=article.link),
                category=item.category,
                creator=item.creator,
                pub_date=item.pub_date,
            )
            expanded_items.append(new_item)

        return expanded_items
    except Exception as e:
        logger.error(f"Failed to expand digest {item.link}: {e}")
        return []


async def refresh_feed(session: aiohttp.ClientSession, feed: Feed) -> None:
    """Refresh a single feed."""
    try:
        url = f"{TLDR_BASE_URL}/{feed.url_path}"
        content = await fetch(session, url)
        rss = Rss.from_xml(content)

        # Expand all digest items sequentially to avoid rate-limiting
        all_items: list[Item] = []
        for item in rss.channel.items:
            expanded_items = await expand_digest_item(session, item, feed)
            all_items.extend(expanded_items)
            await asyncio.sleep(1)

        # Filter expanded items (remove sponsors from individual articles)
        rss.channel.items = list(filter_items(all_items))
        feeds[feed] = rss
        print(f"Refreshed {feed.value}: {len(rss.channel.items)} articles")
    except Exception as e:
        logger.error(f"Failed to refresh {feed.value}: {e}")


async def refresh_all_feeds() -> None:
    async with aiohttp.ClientSession() as session:
        # Refresh all feeds sequentially with a delay to avoid rate limiting
        for feed in Feed:
            await refresh_feed(session, feed)
            await asyncio.sleep(1)



def get_feed(feed_path: str) -> Rss | None:
    for feed in Feed:
        if feed.url_path == feed_path:
            return feeds.get(feed)
    return None
