# Datasets and ML planning

pytcrf turns The Cutting Room Floor into a game-preservation corpus. The
headline artifact is the `pages` dataset: one row per
`(game, platform, section, text)`, where each section is a documented chunk
of unused, cut, regional, or debug content. It is the metadata counterpart
to the `pyromhacking` corpus. Together they cover what was removed (TCRF)
and what the community changed back in or modified (romhacking).

## What this client produces

### 1. `pages`: section corpus (headline)

One row per `(game, platform, section)`, from
`pytcrf.dataset.iter_page_rows` / `build_pages_dataset`:

| Column | Type | Notes |
|---|---|---|
| `game` | string | page title: the `tcrf_title` join key |
| `platform` | string | from the `Category:Games` tree (`Genesis`, `NES`, …) |
| `pageid` | int | MediaWiki page id |
| `section` | string | heading line (`Debug Mode`, `Unused Graphics`, …) |
| `level` | int | heading depth |
| `anchor` | string | section fragment id |
| `is_notable` | bool | flags cut/unused/regional/debug content |
| `text` | string | plain extracted section body |
| `url` | string | canonical page URL |

A game on multiple platforms emits its row set once per platform, so the
table joins cleanly on `platform`. `notable_only=True` keeps only the
preservation-relevant sections.

### 2. `games`: page index

One row per game page: `tcrf_title`, `platforms`, `pageid`, top-level
section headings, and notable-section headings. Produced from `iter_games`
plus `ids.game_to_extra`.

### 3. `platforms`: platform vocabulary

The controlled list of platforms TCRF organises games by
(`pytcrf.list_platforms()`), a small normalisation gazetteer.

## Suggested Hugging Face configs

A single dataset repo can hold multiple configs:

| Config | Source | Publish? |
|---|---|---|
| `pages` | `build_pages_dataset(...)` | Yes: the corpus and the RAG/training source |
| `games` | `iter_games` + `game_to_extra` | Yes: compact page index |
| `platforms` | `list_platforms()` | Yes (small): controlled vocabulary |

All configs derive from TCRF (CC BY-SA: see
[PROVENANCE.md](../PROVENANCE.md)). Keep its attribution and link back to
each page (`url` is embedded in every row).

## ML tasks served

- **Game-preservation retrieval / RAG**: chunk, embed, and retrieve the
  `pages` corpus to answer "what was cut, unused, or regional in game X."
  pairs with the romhacking corpus for a preservation assistant.
- **Section-type classification**: predict the `is_notable` content type
  (unused, cut, debug, regional, revisional) from section text.
- **Cross-source linking**: join `tcrf_title` against pyromhacking entries
  to connect documented removals with community restorations and mods.
- **Platform NER / normalisation**: the platform vocabulary works as a
  gazetteer.

## Recipe

```python
from pytcrf import dataset

# validate on a small, polite sample first
n = dataset.build_pages_dataset("tcrf_pages.jsonl",
                                platforms=["Genesis"], per_platform_limit=3,
                                notable_only=True)
print(n, "rows")

# stream rows for custom processing
for row in dataset.iter_page_rows(platforms=["NES"], per_platform_limit=1):
    ...

# full run (treat as a homelab job: raise the delay, drop the limits)
# from pytcrf import TCRF
# dataset.build_pages_dataset("tcrf_pages.jsonl",
#                             transport=TCRF(delay=2.0).transport)
```

`iter_page_rows` makes one API call per section per page, so the corpus is
large. Sample before you run a full crawl. See
`examples/06_dataset_export.py`.

---
[← Transport and the scraper trap](advanced.md) · [Home](../README.md)
