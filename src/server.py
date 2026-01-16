import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from lxml import etree

from src.client import get_feed, refresh_all_feeds, Feed


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: Print available feeds
    for feed in Feed:
        print(f"{feed.value}: /feed/{feed.url_path}.rss")

    # Start background refresh task
    task: asyncio.Task[None] = asyncio.create_task(background_refresh())
    yield

    # Shutdown
    task.cancel()


async def background_refresh() -> None:
    while True:
        await refresh_all_feeds()
        await asyncio.sleep(24 * 60 * 60)  # 24 hours


app = FastAPI(title="TLDR RSS Proxy", lifespan=lifespan)


@app.get("/feeds")
async def list_feeds() -> dict[str, list[str]]:
    return {"feeds": [feed.url_path for feed in Feed]}


@app.get("/feed/{feed_name}.rss")
async def serve_feed(feed_name: str) -> Response:
    valid_paths = [feed.url_path for feed in Feed]
    if feed_name not in valid_paths:
        raise HTTPException(status_code=404, detail=f"Feed '{feed_name}' not found. Available: {valid_paths}")

    rss = get_feed(feed_name)
    if rss is None:
        raise HTTPException(status_code=503, detail="Feed not yet loaded")

    tree = rss.to_xml_tree()
    xml_bytes: bytes = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8')
    return Response(content=xml_bytes, media_type="application/rss+xml; charset=utf-8")
