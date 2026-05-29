# API reference

Everything below is re-exported from the top-level `pytcrf` package.

## Lookup functions

### `get_game(title, *, with_wikitext=False, with_section_text=False, platforms=None, transport=None) -> GamePage | None`

Fetch one article's section structure via `action=parse`. Returns `None` when
the page does not exist.

- `with_wikitext` — also return the raw page wikitext (enables infobox platform
  detection). Wikitext is fetched by default unless you supply `platforms` for a
  heavy section-text crawl.
- `with_section_text` — fetch and attach plain text to every `Section` (one
  extra API call per section).
- `platforms` — override the platform list (otherwise inferred from the infobox).

### `get_section_text(title, section_index, *, transport=None) -> str`

Plain text of a single section by its MediaWiki section index.

### `load_sections(page, *, transport=None) -> GamePage`

Fetch and attach `text` to every section of an existing `GamePage`, in place.

## Enumeration

### `list_platforms(*, transport=None) -> List[str]`

The platform names under `Category:Games by platform` (e.g. `Genesis`, `NES`).

### `iter_games(*, platforms=None, per_platform_limit=None, transport=None) -> Iterator[GamePage]`

Walk the `Category:Games` tree, yielding **section-less** `GamePage` stubs with
`title`, `pageid` and detected `platforms`. Call `get_game` per stub for the
structure. A page found under several platforms is yielded once with all its
platforms merged.

### `iter_platform_categories(*, limit=None, transport=None) -> Iterator[CategoryMember]`

The per-platform leaf categories (`Category:<platform> games`).

### `iter_platform_games(platform_category, *, limit=None, transport=None) -> Iterator[CategoryMember]`

The game *pages* (namespace 0) in one platform category.

### `iter_category_members(category, *, member_type=None, limit=None, transport=None) -> Iterator[CategoryMember]`

Generic `categorymembers` walk with transparent continuation. `member_type` is
`"page"`, `"subcat"` or `"file"`.

## Models

### `GamePage`

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | the `tcrf_title` anchor |
| `pageid` | `int \| None` | MediaWiki page id |
| `platforms` | `List[str]` | from the category tree / infobox |
| `sections` | `List[Section]` | the article's heading tree |
| `wikitext` | `str \| None` | raw page wikitext (when fetched) |

Properties: `url`, `notable_sections`. Methods: `to_dict()`,
`from_parse(node, platforms=…)`.

### `Section`

| Field | Type | Notes |
|---|---|---|
| `index` | `str` | MediaWiki section index (for `parse&section=`) |
| `level` | `int` | heading depth (`2` == `==H2==`) |
| `line` | `str` | rendered heading text |
| `anchor` | `str` | fragment id |
| `text` | `str \| None` | plain body (when loaded) |

Properties: `is_notable` (heading flags cut/unused/regional/debug content).
Methods: `to_dict()`, `from_api(node)`.

### `CategoryMember`

`title`, `pageid`, `ns`. Properties: `is_subcategory` (ns 14), `url`.

## Identity

### `pytcrf.ids.game_to_extra(game) -> dict`

Convert a `GamePage` to a mediavocab `ExternalIds.extra` dict. Canonical anchor
is `tcrf_title`. Other keys: `tcrf_url`, `tcrf_pageid`, `tcrf_platforms` (JSON),
`tcrf_sections` (JSON), `tcrf_notable_sections` (JSON).

### `pytcrf.ids.canonical_id(game) -> str`

The `tcrf_title` anchor.

## Transport

### `Transport(*, mode=None, flaresolverr_url=None, flaresolverr_timeout_ms=None, wayback_fallback=None, delay=1.0)`

See [advanced.md](advanced.md). `ScraperBlocked` is raised when TCRF serves its
anti-scraper trap for a module.

### `TCRF(transport=None, *, flaresolverr_url=None, wayback=False, delay=1.0)`

High-level client binding every method to one configured transport.

## Dataset

`pytcrf.dataset` — see [dataset.md](dataset.md): `iter_page_rows`, `page_to_rows`,
`export_jsonl`, `build_pages_dataset`.
