"""Converters from pytcrf models to flat ``str -> str`` external-ID dicts.

The canonical anchor is ``tcrf_title`` — the MediaWiki page title, which is the
stable identity of a TCRF article (the same key pyromhacking joins against for
game-preservation cross-references).

Key namespace
-------------
Game page:
    ``tcrf_title``            — canonical page title (anchor)
    ``tcrf_url``              — canonical page URL
    ``tcrf_pageid``           — MediaWiki page id (int as string)
    ``tcrf_platforms``        — JSON array of platform names
    ``tcrf_sections``         — JSON array of top-level section heading lines
    ``tcrf_notable_sections`` — JSON array of cut/unused/regional/debug headings
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from pytcrf.models import GamePage


def game_to_extra(game: "GamePage") -> Dict[str, str]:
    """Convert a :class:`~pytcrf.models.GamePage` to a flat ``str -> str`` external-ID dict."""
    extra: Dict[str, str] = {
        "tcrf_title": game.title,
        "tcrf_url": game.url,
    }
    if game.pageid is not None:
        extra["tcrf_pageid"] = str(game.pageid)
    if game.platforms:
        extra["tcrf_platforms"] = json.dumps(game.platforms, ensure_ascii=False)

    top = [s.line for s in game.sections if s.level <= 2 and s.line]
    if top:
        extra["tcrf_sections"] = json.dumps(top, ensure_ascii=False)

    notable = [s.line for s in game.notable_sections if s.line]
    if notable:
        extra["tcrf_notable_sections"] = json.dumps(notable, ensure_ascii=False)

    return extra


def canonical_id(game: "GamePage") -> str:
    """Return the canonical ``tcrf_title`` anchor for *game*."""
    return game.title


__all__ = ["game_to_extra", "canonical_id"]
