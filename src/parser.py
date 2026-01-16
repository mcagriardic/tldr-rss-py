import logging
import re
from dataclasses import dataclass

from lxml import html

logger = logging.getLogger(__name__)


@dataclass
class Article:
    title: str
    link: str
    description: str


def parse_tldr_page(content: bytes) -> list[Article]:
    """Parse a TLDR newsletter page and extract individual articles."""
    articles: list[Article] = []

    try:
        # Decode the content to a string before parsing
        decoded_content = content.decode("utf-8")
        tree = html.fromstring(decoded_content)
        article_elements = tree.xpath("//article")

        for article_el in article_elements:
            # Get the link and title
            link_els = article_el.xpath(".//a[@href]")
            if not link_els:
                continue

            link = link_els[0].get("href", "")
            # Skip empty links, anchor links, or non-http links
            if not link or link.startswith("#") or not link.startswith(("http://", "https://")):
                continue

            # Get title from h3 inside the link
            title_els = article_el.xpath(".//a//h3/text()")
            title = title_els[0].strip() if title_els else ""
            if not title:
                continue

            # Get description from newsletter-html div
            desc_els = article_el.xpath(".//div[contains(@class, 'newsletter-html')]")
            description = ""
            if desc_els:
                description = desc_els[0].text_content().strip()

            # Clean up the link (remove tracking params)
            link = clean_url(link)

            articles.append(Article(title=title, link=link, description=description))

    except Exception as e:
        logger.error(f"Failed to parse TLDR page: {e}")

    return articles


def clean_url(url: str) -> str:
    """Clean URL but keep utm_source for TLDR attribution."""
    # Remove utm params except utm_source
    url = re.sub(r"[?&]utm_(?!source)[^&]*", "", url)
    return url.rstrip("?&")
