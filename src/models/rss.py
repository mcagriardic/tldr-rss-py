from typing import Optional
from pydantic_xml import BaseXmlModel, attr, element
from pydantic import HttpUrl


class Guid(BaseXmlModel, tag='guid', search_mode='unordered'):
    is_perma_link: bool = attr(name='isPermaLink')
    value: str


class Image(BaseXmlModel, tag='image', search_mode='unordered'):
    url: str = element()
    title: str = element()
    link: str = element()


class AtomLink(BaseXmlModel, tag='link', nsmap={'': 'http://www.w3.org/2005/Atom'}):
    href: str = attr()
    rel: str = attr()
    type: str = attr()


class Item(BaseXmlModel, tag='item', search_mode='unordered', nsmap={'dc': 'http://purl.org/dc/elements/1.1/'}):
    title: str = element()
    link: HttpUrl = element()
    guid: Guid = element()
    category: str = element()
    creator: str = element(tag='creator', ns='dc')
    pub_date: str = element(tag='pubDate')


class Channel(BaseXmlModel, tag='channel', search_mode='unordered', nsmap={'dc': 'http://purl.org/dc/elements/1.1/'}):
    title: str = element()
    description: str = element()
    link: HttpUrl = element()
    image: Optional[Image] = element(default=None)
    generator: Optional[str] = element(default=None)
    last_build_date: Optional[str] = element(tag='lastBuildDate', default=None)
    pub_date: Optional[str] = element(tag='pubDate', default=None)
    language: Optional[str] = element(default=None)
    managing_editor: Optional[str] = element(tag='managingEditor', default=None)
    web_master: Optional[str] = element(tag='webMaster', default=None)
    ttl: Optional[int] = element(default=None)
    category: Optional[str] = element(default=None)
    items: list[Item] = element(tag='item', default=[])


class Rss(BaseXmlModel, tag='rss', search_mode='unordered'):
    version: str = attr()
    channel: Channel = element()

    class Config:
        xml_namespaces = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'atom': 'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }
