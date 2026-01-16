import logging
from collections.abc import Iterator

from src.models.rss import Item

logger = logging.getLogger(__name__)


def is_excluded_title(item: Item) -> bool:
    title_skip_list = ["sponsor", "tldr"]
    return any(title_skip in item.title.lower() for title_skip in title_skip_list)


def filter_items(items: list[Item]) -> Iterator[Item]:
    for item in items:
        if is_excluded_title(item):
            logger.debug(f"Skipping excluded title: {item}")
            continue
        yield item
