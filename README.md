# tldr-rss-py

Opinionated RSS proxy for TLDR newsletters that expands digest emails into individual article items, filters out sponsors, and prefixes titles with feed names.

Python alternative to [Bullrich/tldr-rss](https://github.com/Bullrich/tldr-rss) (TypeScript).

## Available Feeds

- `/feed/tech.rss`
- `/feed/ai.rss`
- `/feed/devops.rss`
- `/feed/data.rss`

## Docker

```bash
docker build -t tldr-rss .
docker run -p 8000:8000 tldr-rss
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m src.main
```

Server runs at `http://localhost:8800` with hot reload.

## Adding Feeds

Edit the `Feed` enum in [src/client.py](src/client.py):

```python
class Feed(StrEnum):
    TECH = "Tech"
    AI = "AI"
    # Add more from https://tldr.tech/newsletters
```

## Filtering

Items are filtered by title keywords in [src/filters.py](src/filters.py). By default, items containing "sponsor" or "tldr" are excluded.

Article titles are prefixed with the feed name (e.g. `[Tech] Article Title`) to differentiate sources at a glance in feed readers like Karakeep.

## Linting

```bash
pip install -r requirements-dev.txt
ruff check .
```
