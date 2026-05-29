"""Game-page lookup and enumeration backed by the tcrf.net MediaWiki API.

Enumeration walks the **``Category:Games`` tree** rather than ``list=allpages``
(which tcrf.net traps for scrapers — see :mod:`pytcrf.transport`). The tree is::

    Category:Games
      └─ Category:Games by platform
           └─ Category:Genesis games        (a platform leaf)
                └─ Sonic the Hedgehog (Genesis)   (an actual game page)

So :func:`iter_platform_categories` yields the per-platform leaf categories, and
:func:`iter_games` walks them, attaching the platform name to each page.
:func:`get_game` fetches one article's section structure (and optionally its
section text and wikitext) via ``action=parse``.
"""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from pytcrf._clean import platform_from_category
from pytcrf._parse import platforms_from_wikitext, section_html_to_text
from pytcrf.models import CategoryMember, GamePage, Section
from pytcrf.transport import Transport, default_transport

GAMES_CATEGORY = "Category:Games"
GAMES_BY_PLATFORM = "Category:Games by platform"


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


# -- category enumeration -------------------------------------------------

def iter_category_members(category: str, *, member_type: Optional[str] = None,
                          limit: Optional[int] = None,
                          transport: Optional[Transport] = None
                          ) -> Iterator[CategoryMember]:
    """Yield members of *category*, following API continuation transparently.

    Args:
        category:    e.g. ``"Category:Genesis games"``.
        member_type: ``"page"``, ``"subcat"`` or ``"file"`` to filter; ``None``
                     yields everything.
        limit:       stop after this many members (across continuation pages).
    """
    t = _t(transport)
    if not category.lower().startswith("category:"):
        category = f"Category:{category}"
    cont: Dict[str, Any] = {}
    yielded = 0
    while True:
        params: Dict[str, Any] = {
            "action": "query", "list": "categorymembers",
            "cmtitle": category, "cmlimit": "500",
        }
        if member_type:
            params["cmtype"] = member_type
        params.update(cont)
        data = t.api(params)
        for node in data.get("query", {}).get("categorymembers", []):
            yield CategoryMember.from_api(node)
            yielded += 1
            if limit is not None and yielded >= limit:
                return
        cont = data.get("continue", {})
        if not cont:
            return


def iter_platform_categories(*, limit: Optional[int] = None,
                             transport: Optional[Transport] = None
                             ) -> Iterator[CategoryMember]:
    """Yield the per-platform leaf categories under ``Games by platform``."""
    yield from iter_category_members(GAMES_BY_PLATFORM, member_type="subcat",
                                     limit=limit, transport=transport)


def list_platforms(*, transport: Optional[Transport] = None) -> List[str]:
    """Return the list of platform names TCRF organises games by.

    Example::

        import pytcrf
        plats = pytcrf.list_platforms()
        print(len(plats), plats[:5])
    """
    return [platform_from_category(c.title)
            for c in iter_platform_categories(transport=transport)]


def iter_platform_games(platform_category: str, *, limit: Optional[int] = None,
                        transport: Optional[Transport] = None
                        ) -> Iterator[CategoryMember]:
    """Yield the game *pages* (ns 0) in one platform category."""
    yield from iter_category_members(platform_category, member_type="page",
                                     limit=limit, transport=transport)


def iter_games(*, platforms: Optional[List[str]] = None,
               per_platform_limit: Optional[int] = None,
               transport: Optional[Transport] = None
               ) -> Iterator[GamePage]:
    """Walk the ``Category:Games`` tree, yielding section-less :class:`GamePage`.

    Each yielded page carries its ``title``/``pageid`` and the detected
    ``platforms`` (from the category it was found under). Sections are *not*
    fetched here — call :func:`get_game` (or :func:`load_sections`) per page when
    you need the structure, to keep enumeration cheap.

    Args:
        platforms:           restrict to these platform names (case-insensitive);
                             ``None`` walks every platform.
        per_platform_limit:  cap pages taken from each platform (sampling).

    Example::

        import pytcrf
        for g in pytcrf.iter_games(platforms=["Genesis"], per_platform_limit=3):
            print(g.platforms, g.title)
    """
    t = _t(transport)
    wanted = {p.lower() for p in platforms} if platforms else None
    seen: Dict[str, GamePage] = {}
    for cat in iter_platform_categories(transport=t):
        plat = platform_from_category(cat.title)
        if wanted is not None and plat.lower() not in wanted:
            continue
        for member in iter_platform_games(cat.title, limit=per_platform_limit,
                                          transport=t):
            if member.is_subcategory:
                continue
            existing = seen.get(member.title)
            if existing is not None:
                if plat not in existing.platforms:
                    existing.platforms.append(plat)
                continue
            page = GamePage(title=member.title, pageid=member.pageid,
                            platforms=[plat])
            seen[member.title] = page
            yield page


# -- single page ----------------------------------------------------------

def get_game(title: str, *, with_wikitext: bool = False,
             with_section_text: bool = False,
             platforms: Optional[List[str]] = None,
             transport: Optional[Transport] = None) -> Optional[GamePage]:
    """Fetch one game article's section structure.

    Args:
        title:             the page title (the ``tcrf_title`` anchor).
        with_wikitext:     also fetch the raw page wikitext (enables infobox
                           platform detection when *platforms* is not given).
        with_section_text: fetch and attach plain text for every section (one
                           extra API call per section — use for corpus builds).
        platforms:         override the platform list (otherwise inferred from
                           the wikitext infobox when *with_wikitext*).

    Returns ``None`` when the page does not exist.

    Example::

        import pytcrf
        g = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
        print([s.line for s in g.notable_sections])
    """
    t = _t(transport)
    props = ["sections"]
    if with_wikitext or (platforms is None and with_section_text is False):
        # wikitext is cheap and gives platform fallback; always grab it unless
        # the caller is doing a heavy section-text crawl and supplied platforms.
        props.append("wikitext")
    data = t.api({"action": "parse", "page": title, "prop": "|".join(props)})
    parse = data.get("parse")
    if not parse:
        return None
    page = GamePage.from_parse(parse, platforms=platforms)
    if not page.platforms and page.wikitext:
        page.platforms = platforms_from_wikitext(page.wikitext)
    if with_section_text:
        load_sections(page, transport=t)
    return page


def load_sections(page: GamePage, *, transport: Optional[Transport] = None
                  ) -> GamePage:
    """Fetch and attach plain text to each :class:`Section` of *page* in place.

    One ``action=parse&prop=text&section=<index>`` call per section. Mutates and
    returns *page*.
    """
    t = _t(transport)
    for sec in page.sections:
        if not sec.index:
            continue
        data = t.api({"action": "parse", "page": page.title,
                      "prop": "text", "section": sec.index})
        html = (data.get("parse", {}).get("text") or {}).get("*", "")
        sec.text = section_html_to_text(html)
    return page


def get_section_text(title: str, section_index: str, *,
                     transport: Optional[Transport] = None) -> str:
    """Fetch the plain text of a single section of a page by its index."""
    t = _t(transport)
    data = t.api({"action": "parse", "page": title, "prop": "text",
                  "section": section_index})
    html = (data.get("parse", {}).get("text") or {}).get("*", "")
    return section_html_to_text(html)


class TCRF:
    """High-level client binding every call to one configured transport.

    Mirrors the module-level functions. Use it to share a single polite
    :class:`Transport` (delay, mode) across a whole crawl.

    Example::

        import pytcrf
        client = pytcrf.TCRF(delay=1.5)
        g = client.get_game("Sonic the Hedgehog (Genesis)")
    """

    def __init__(self, transport=None, *, flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback: bool = False,
                 wayback_fallback: Optional[bool] = None,
                 delay: float = 1.0) -> None:
        if isinstance(transport, Transport):
            self.transport = transport
        else:
            mode = "wayback" if wayback else transport
            self.transport = Transport(
                mode=mode, flaresolverr_url=flaresolverr_url,
                flaresolverr_timeout_ms=flaresolverr_timeout_ms,
                wayback_fallback=wayback_fallback, delay=delay)

    def list_platforms(self) -> List[str]:
        return list_platforms(transport=self.transport)

    def iter_games(self, *, platforms=None, per_platform_limit=None):
        return iter_games(platforms=platforms,
                          per_platform_limit=per_platform_limit,
                          transport=self.transport)

    def iter_category_members(self, category, *, member_type=None, limit=None):
        return iter_category_members(category, member_type=member_type,
                                     limit=limit, transport=self.transport)

    def get_game(self, title, *, with_wikitext=False, with_section_text=False,
                 platforms=None) -> Optional[GamePage]:
        return get_game(title, with_wikitext=with_wikitext,
                        with_section_text=with_section_text, platforms=platforms,
                        transport=self.transport)

    def get_section_text(self, title, section_index) -> str:
        return get_section_text(title, section_index, transport=self.transport)


__all__ = [
    "GAMES_CATEGORY", "GAMES_BY_PLATFORM",
    "iter_category_members", "iter_platform_categories", "list_platforms",
    "iter_platform_games", "iter_games", "get_game", "load_sections",
    "get_section_text", "TCRF",
]
