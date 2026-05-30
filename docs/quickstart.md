# Quickstart

## Install

```bash
pip install pytcrf[stealth]
```

The `stealth` extra pulls in `curl-cffi` for TLS impersonation — recommended
for reliable connections and consistent with how browsers reach the API.

## A single game

```python
import pytcrf

game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
print(game.title)         # Sonic the Hedgehog (Genesis)
print(game.pageid)        # 1583
print(game.platforms)     # ['Genesis']  (read from the {{bob}} infobox)

# the section tree IS the documented content map
for s in game.sections:
    print("  " * (s.level - 2) + s.line)

# just the cut/unused/regional/debug headings
for s in game.notable_sections:
    print(s.line)
```

`get_game` fetches the section *structure* only (one API call). To pull the
plain text of every section (one call per section), ask for it:

```python
game = pytcrf.get_game("Sonic the Hedgehog (Genesis)", with_section_text=True)
for s in game.notable_sections:
    print(f"## {s.line}\n{s.text[:200]}\n")
```

## Browsing by platform

```python
import pytcrf

# every platform TCRF organises games by
print(pytcrf.list_platforms())

# game pages on one platform (cheap stubs — no sections yet)
for g in pytcrf.iter_games(platforms=["NES"], per_platform_limit=5):
    print(g.title)
```

`iter_games` is a generator that walks the `Category:Games` tree. Use
`per_platform_limit` while exploring so you don't enumerate thousands of pages.

## A shared, polite client

```python
import pytcrf

client = pytcrf.TCRF(delay=1.5)        # 1.5 s between API calls
for g in client.iter_games(platforms=["Genesis"], per_platform_limit=3):
    full = client.get_game(g.title)
    print(full.title, len(full.notable_sections), "notable sections")
```

One `TCRF` shares a single transport (and its delay) across the whole crawl.

## Serialising

```python
import json
from pytcrf.ids import game_to_extra

game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
print(json.dumps(game.to_dict())[:200])
print(game_to_extra(game)["tcrf_title"])   # the canonical external-id anchor
```

Next: [api.md](api.md) for the full surface, [dataset.md](dataset.md) to build a
corpus, [advanced.md](advanced.md) for transport, the Referer requirement, and the scraper trap.
