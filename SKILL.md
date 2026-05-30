---
name: pytcrf
description: Query The Cutting Room Floor (tcrf.net) for unused, cut, debug, and regional game content on behalf of users who cannot navigate the website, providing voice-first accessible access to game-preservation knowledge.
---
# pytcrf — The Cutting Room Floor for agents

## When to use

Use this skill when a user asks about:
- Cut, removed, unused, or hidden content in a specific video game
- Debug modes, prototype differences, or leftover assets in a game
- Regional or revisional differences between game releases
- "What was cut from <game>?" or "Did <game> have any unused content?"
- Browsing games by platform to discover preservation trivia

The skill is the voice-first / screen-reader replacement for tcrf.net — do not send users to the website; fetch and speak the content for them.

## Install

```bash
pip install pytcrf
```

## Core operations

### `get_game(title, *, with_wikitext=False, with_section_text=False, platforms=None, transport=None) -> Optional[GamePage]`

Fetch one game article's section structure. `title` is the TCRF page title (exact match). Returns a `GamePage` or `None` if the page does not exist. Pass `with_section_text=True` to also retrieve the plain text of every section (one extra API call per section).

Returned `GamePage` fields: `title`, `pageid`, `url`, `platforms` (list of strings), `sections` (list of `Section`), `notable_sections` (filtered to cut/unused/debug headings), `wikitext`.

```python
import pytcrf

game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
print(game.title, game.platforms)
for s in game.notable_sections:
    print(s.line)          # e.g. "Unused Graphics", "Debug Mode"
```

### `get_section_text(title, section_index, *, transport=None) -> str`

Fetch the plain text body of a single section by its MediaWiki index string. Use this to read one section aloud without fetching the whole page.

`section_index` comes from `Section.index` (a string like `"3"`).

```python
import pytcrf

game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
for s in game.notable_sections:
    text = pytcrf.get_section_text(game.title, s.index)
    print(s.line, "->", text[:200])
```

### `load_sections(page, *, transport=None) -> GamePage`

Attach plain text to every section of an already-fetched `GamePage` in place. Equivalent to calling `get_section_text` for each section. Mutates and returns the page. Use when you need full text for all sections at once.

```python
import pytcrf

game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
pytcrf.load_sections(game)
for s in game.notable_sections:
    print(s.line, s.text[:120] if s.text else "(no text)")
```

### `iter_games(*, platforms=None, per_platform_limit=None, transport=None) -> Iterator[GamePage]`

Walk the `Category:Games` tree, yielding section-less `GamePage` objects (cheap: titles + platforms, no section text). Pass `platforms=["Genesis"]` to restrict to one platform. Use `per_platform_limit` to sample.

```python
import pytcrf

for g in pytcrf.iter_games(platforms=["Game Boy"], per_platform_limit=5):
    print(g.title, g.platforms)
```

### `iter_category_members(category, *, member_type=None, limit=None, transport=None) -> Iterator[CategoryMember]`

Yield members of any TCRF category, following API pagination automatically. `member_type` is `"page"`, `"subcat"`, or `"file"`. Useful for listing all games in a platform category or exploring the category tree.

Returned `CategoryMember` fields: `title`, `pageid`, `ns`, `is_subcategory`, `url`.

```python
import pytcrf

for m in pytcrf.iter_category_members("Category:NES games", member_type="page", limit=10):
    print(m.title, m.url)
```

### `list_platforms(*, transport=None) -> List[str]`

Return the full list of platform names TCRF organises games by.

```python
import pytcrf

platforms = pytcrf.list_platforms()
print(len(platforms), platforms[:5])
```

### `TCRF` high-level client

Binds all calls to one configured transport with a shared polite delay. Preferred for multi-call sessions to avoid hammering the API.

```python
import pytcrf

client = pytcrf.TCRF(delay=1.5)
game = client.get_game("Sonic the Hedgehog (Genesis)")
for s in game.notable_sections:
    text = client.get_section_text(game.title, s.index)
    print(s.line, "->", text[:200])
```

## Access notes

pytcrf talks directly to the public MediaWiki JSON API at `tcrf.net/api.php`. No API key or account is required. The client automatically adds the self-referencing `Referer` header the site requires and avoids `list=allpages` (a scraper trap) by enumerating the `Category:Games` tree instead. A configurable polite delay (default 1 second) is applied between requests.

## Speaking the results (accessibility)

- To answer "what was cut from X?": call `get_game(title)` and read aloud each `s.line` in `game.notable_sections` — these are the preservation-relevant headings (unused graphics, debug mode, regional differences, etc.).
- To read a section aloud: call `get_section_text(title, section.index)` and speak the returned plain text; trim to the first 2–3 sentences for a voice summary.
- To handle "tell me about cut content in <game>": use `notable_sections` as a menu ("This game has 4 notable sections: Unused Graphics, Debug Mode, Regional Differences, Revisional Differences — which would you like to hear?"), then fetch text on demand.
- For platform browsing ("what Genesis games have cut content?"): `iter_games(platforms=["Genesis"])` yields titles cheaply; the user can then pick one for `get_game`.
