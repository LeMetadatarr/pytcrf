# AGENTS.md — pytcrf

Typed Python client for **The Cutting Room Floor** (`tcrf.net`), the MediaWiki of
unused/cut/regional/debug game content. Talks **directly to the MediaWiki JSON
API**. Game-preservation corpus; pairs with `pyromhacking`.

## Layout

| Path | Role |
|---|---|
| `pytcrf/__init__.py` | public API surface |
| `pytcrf/transport.py` | `Transport` over `unblock_requests.CloudflareSession`; the `api()` referer/scraper-trap logic |
| `pytcrf/_clean.py` | text + category-title normalisation (stdlib only) |
| `pytcrf/_parse.py` | section-HTML → text, infobox-wikitext → platforms (BeautifulSoup) |
| `pytcrf/models.py` | `GamePage`, `Section`, `CategoryMember` dataclasses |
| `pytcrf/games.py` | lookup + `Category:Games` enumeration; `TCRF` client |
| `pytcrf/ids.py` | `ExternalIds.extra` converter; anchor `tcrf_title` |
| `pytcrf/dataset.py` | `(game, platform, section, text)` rows + `export_jsonl` |
| `pytcrf/version.py` | version (do not edit) |
| `tests/` | offline fixture tests + one live smoke (`-m live`) |
| `docs/`, `examples/` | docs and runnable scripts |

## Hard rules (TCRF-specific)

- **Every API call needs a self-referencing `Referer` header.** Without it the
  site returns a 403 interstitial. `Transport.api` does this — never bypass it
  with a raw session call.
- **Never use `list=allpages`.** TCRF answers it with a multi-megabyte
  `"invalid response for scrapers"` trap. Enumerate via `list=categorymembers`
  (the `Category:Games` tree). `Transport.api` raises `ScraperBlocked` if a trap
  body slips through.
- **`Category:Games` holds only subcategories** — real game pages live at
  `Games by platform → <platform> games → page`. That path also yields the
  platform for free.
- HTTP only through `unblock_requests`; no headed browser.

## Conventions

- Commit identity `JarbasAi <jarbasai@mailfence.com>`; branches `master`/`dev`,
  GitHub default `dev`; never `main`. Private repo under **TigreGotico**.
- Never edit `version.py` (initial `0.0.1` only here; CI bumps via commit prefix).
- No `.github/workflows` yet — see `TODO.md`.

## Test

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -m "not live"   # offline (workspace has a broken plugin)
pytest -m live                                          # hits tcrf.net
```

Offline tests run against real captured API fixtures in `tests/fixtures/`.
