"""pytcrf — typed Python client for The Cutting Room Floor (tcrf.net).

The Cutting Room Floor is a MediaWiki documenting the **unused, cut, regional
and debug content** of individual video games — leftover graphics, hidden debug
menus, prototype differences, revisional and regional changes. pytcrf talks
**directly to its MediaWiki JSON API** (``tcrf.net/api.php``) behind typed
dataclasses, and turns it into a game-preservation corpus that pairs with
pyromhacking.

The wiki guards its API: requests without a self-referencing ``Referer`` hit an
interstitial, and ``list=allpages`` is a scraper trap. pytcrf handles the first
transparently and sidesteps the second by enumerating the ``Category:Games``
tree (see :mod:`pytcrf.transport`).

Quick start::

    import pytcrf

    # the platforms TCRF organises games by
    plats = pytcrf.list_platforms()

    # walk games on a platform (cheap: titles + platform, no sections yet)
    for g in pytcrf.iter_games(platforms=["Genesis"], per_platform_limit=3):
        print(g.platforms, g.title)

    # one game's section structure (the cut/unused/debug content map)
    game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
    print(game.title, game.platforms)
    for s in game.notable_sections:
        print(" ", s.line)

    # canonical external-id anchor
    from pytcrf.ids import game_to_extra
    game_to_extra(game)["tcrf_title"]      # 'Sonic the Hedgehog (Genesis)'

Build the ``(game, platform, section, text)`` dataset with
:mod:`pytcrf.dataset` — the retrieval/training source for game-preservation work.
"""
from pytcrf.models import (
    CategoryMember,
    GamePage,
    Section,
    page_url,
)
from pytcrf.games import (
    GAMES_BY_PLATFORM,
    GAMES_CATEGORY,
    TCRF,
    get_game,
    get_section_text,
    iter_category_members,
    iter_games,
    iter_platform_categories,
    iter_platform_games,
    list_platforms,
    load_sections,
)
from pytcrf.transport import ScraperBlocked, Transport
from pytcrf.version import __version__

__all__ = [
    "GamePage",
    "Section",
    "CategoryMember",
    "page_url",
    "TCRF",
    "Transport",
    "ScraperBlocked",
    "get_game",
    "get_section_text",
    "load_sections",
    "iter_games",
    "iter_category_members",
    "iter_platform_categories",
    "iter_platform_games",
    "list_platforms",
    "GAMES_CATEGORY",
    "GAMES_BY_PLATFORM",
    "__version__",
]
