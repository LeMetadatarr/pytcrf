# pytcrf

Typed Python client for [The Cutting Room Floor](https://tcrf.net) (TCRF): a
MediaWiki that documents the unused, cut, regional, and debug content of
individual video games: leftover graphics, hidden debug menus, prototype
differences, and revisional and regional changes.

pytcrf talks directly to the TCRF MediaWiki JSON API (`tcrf.net/api.php`)
behind typed dataclasses. It enumerates games through the `Category:Games`
tree, parses each article's section structure, and exports a
game-preservation corpus of `(game, platform, section, text)` rows. It is the
metadata counterpart to [pyromhacking](https://github.com/LeMetadatarr/pyromhacking).

## Install

```bash
pip install pytcrf
pip install pytcrf[stealth]   # adds curl-cffi: recommended (see below)
pip install pytcrf[test]      # adds pytest
```

> **Site behaviors handled:** TCRF has two documented quirks. (1) A referer
> interstitial: a request without a `Referer` header pointing at the
> requested page gets a 403 asking the user to click "continue." pytcrf sends
> the self-referencing referer on every call, the same as a browser does. (2)
> A scraper trap: `list=allpages` returns a multi-megabyte
> `"invalid response for scrapers"` payload at HTTP 200. pytcrf enumerates the
> `Category:Games` tree instead, and raises `ScraperBlocked` if the trap is
> hit. Everything routes through `unblock_requests` (`CloudflareSession`) for
> uniform, resilient HTTP. See [docs/advanced.md](docs/advanced.md).

## 30-second tour

```python
import pytcrf

# the platforms TCRF organises games by
plats = pytcrf.list_platforms()
print(len(plats), plats[:5])

# walk games on a platform (cheap: titles + platform, sections not fetched yet)
for g in pytcrf.iter_games(platforms=["Genesis"], per_platform_limit=3):
    print(g.platforms, g.title)

# one game's section structure: its cut/unused/regional/debug content map
game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
print(game.title, game.platforms)             # ['Genesis']
for s in game.notable_sections:
    print(" ", s.level, s.line)               # Debug Mode, Unused Sprites, ...

# canonical external-id anchor
from pytcrf.ids import game_to_extra
game_to_extra(game)["tcrf_title"]             # 'Sonic the Hedgehog (Genesis)'
```

## What you can fetch

| Function | Returns | Source |
|---|---|---|
| `list_platforms()` | `List[str]` | `Category:Games by platform` |
| `iter_games(platforms=…)` | `Iterator[GamePage]` | `Category:<platform> games` |
| `iter_category_members(cat)` | `Iterator[CategoryMember]` | `categorymembers` |
| `get_game("…")` | `GamePage` / `None` | `action=parse` (sections) |
| `get_section_text(title, idx)` | `str` | `action=parse&prop=text` |

A `GamePage` carries `title` (the `tcrf_title` anchor), `pageid`, `platforms`,
`sections: List[Section]`, and, when fetched, `wikitext`. Each `Section` has a
`level`, `line`, `anchor`, `is_notable` flag, and (when loaded) plain `text`.

## Dataset

```python
from pytcrf import dataset

# one row per (game, platform, section, text): validate on a small sample first
dataset.build_pages_dataset("tcrf_pages.jsonl",
                            platforms=["Genesis"], per_platform_limit=3,
                            notable_only=True)
```

A game-preservation corpus that pairs with pyromhacking. See
[docs/dataset.md](docs/dataset.md).

## Documentation

- [docs/quickstart.md](docs/quickstart.md): the essentials
- [docs/api.md](docs/api.md): every function and model field
- [docs/categories.md](docs/categories.md): the `Category:Games` tree and enumeration
- [docs/advanced.md](docs/advanced.md): transport, the interstitial, the scraper trap
- [docs/dataset.md](docs/dataset.md): datasets this client produces and the ML tasks they serve
- [PROVENANCE.md](PROVENANCE.md): source, licensing, and polite scraping

## Related projects

- [pyromhacking](https://github.com/LeMetadatarr/pyromhacking): the community
  romhacking counterpart: what was changed back in or modified, versus what
  TCRF documents as removed.

Runnable, numbered scripts live in [examples/](examples/).

## License

Apache-2.0. See [LICENSE](LICENSE).
