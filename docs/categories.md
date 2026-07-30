# The Category:Games tree

pytcrf enumerates games through TCRF's category graph, not `list=allpages`
(the wiki traps that call for scrapers — see [advanced.md](advanced.md)).
Knowing the tree shape makes enumeration predictable.

## Shape

```
Category:Games
  ├─ Category:Games by platform          ← the spine pytcrf walks
  │    ├─ Category:Genesis games          ← a platform leaf
  │    │    ├─ Sonic the Hedgehog (Genesis)   ← an actual game page (ns 0)
  │    │    └─ …
  │    ├─ Category:NES games
  │    └─ … (160+ platforms)
  ├─ Category:Games by developer
  ├─ Category:Games by publisher
  ├─ Category:Games by series
  ├─ Category:Unlicensed games
  ├─ Category:Unreleased games
  └─ …
```

`Category:Games` itself holds only subcategories. No game page lives
directly under it. The reliable path to actual pages is
`Games by platform → <platform> games → page`, which also lets pytcrf
attach a platform to every game for free.

## Walking it

```python
import pytcrf

# the platform leaves
for cat in pytcrf.iter_platform_categories():
    print(cat.title)            # 'Category:Genesis games', …

# pages in one platform
for m in pytcrf.iter_platform_games("Category:Genesis games"):
    print(m.title, m.pageid)

# everything at once, platform attached, de-duplicated across platforms
for g in pytcrf.iter_games(platforms=["Genesis", "NES"], per_platform_limit=5):
    print(g.platforms, g.title)
```

A game released on several systems shows up under multiple platform
categories. `iter_games` yields it once, with every platform merged into
`g.platforms`.

## Other axes

The `categorymembers` walker is generic, so any of the other axes work too:

```python
import pytcrf

for m in pytcrf.iter_category_members("Category:Unlicensed games",
                                      member_type="page", limit=20):
    print(m.title)

for m in pytcrf.iter_category_members("Category:Prototype versions",
                                      member_type="page", limit=20):
    print(m.title)
```

## Continuation

The MediaWiki API caps `cmlimit` at 500. pytcrf follows the `continue` token
for you, so the iterators yield the full membership without you handling
paging. Use `limit` or `per_platform_limit` to stop early while you explore.

---
[← API reference](api.md) · [Home](../README.md) · [Transport and the scraper trap →](advanced.md)
