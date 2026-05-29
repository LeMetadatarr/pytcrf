"""Dataset export for The Cutting Room Floor.

Turns the ``Category:Games`` tree into a flat, ML-ready corpus of **section
rows** — one record per ``(game, platform, section, text)``. This is the
game-preservation counterpart to the romhacking corpus: every row is a chunk of
documented unused/cut/regional/debug content, attributable to its game page.

The headline export is :func:`export_jsonl`, fed by :func:`iter_page_rows`. Both
are resumable-friendly (you stream and checkpoint yourself) and polite (one
shared :class:`Transport` with a delay). A full crawl is large — validate on a
small sample (a couple of platforms, a per-platform limit) before a homelab run.

See ``docs/dataset.md`` for the HF dataset configs and the ML rationale.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, Iterator, List, Optional

from pytcrf.games import get_game, iter_games, load_sections
from pytcrf.models import GamePage
from pytcrf.transport import Transport, default_transport


def page_to_rows(game: GamePage) -> List[Dict[str, Any]]:
    """Flatten one (section-loaded) :class:`GamePage` to ``pages`` rows.

    Emits one row per section: ``{game, platform, pageid, section, level,
    anchor, is_notable, text, url}``. A page with several platforms emits the
    row set once per platform (so the table joins cleanly on ``platform``).
    Sections without extracted ``text`` still yield a row (text == "").
    """
    rows: List[Dict[str, Any]] = []
    platforms = game.platforms or [""]
    for platform in platforms:
        for sec in game.sections:
            rows.append({
                "game": game.title,
                "platform": platform,
                "pageid": game.pageid,
                "section": sec.line,
                "level": sec.level,
                "anchor": sec.anchor,
                "is_notable": sec.is_notable,
                "text": sec.text or "",
                "url": game.url,
            })
    return rows


def iter_page_rows(*, platforms: Optional[List[str]] = None,
                   per_platform_limit: Optional[int] = None,
                   notable_only: bool = False,
                   transport: Optional[Transport] = None
                   ) -> Iterator[Dict[str, Any]]:
    """Stream ``(game, platform, section, text)`` rows across the games tree.

    Walks :func:`pytcrf.iter_games`, fetches each page's sections and section
    text, and yields one row per section.

    Args:
        platforms:          restrict to these platforms; ``None`` walks all.
        per_platform_limit: cap pages per platform (sampling).
        notable_only:       only emit cut/unused/regional/debug sections.

    Example::

        from pytcrf import dataset
        rows = dataset.iter_page_rows(platforms=["Genesis"],
                                      per_platform_limit=2, notable_only=True)
        for r in rows:
            print(r["game"], "|", r["section"])
    """
    t = transport or default_transport()
    for stub in iter_games(platforms=platforms,
                           per_platform_limit=per_platform_limit, transport=t):
        page = get_game(stub.title, with_section_text=True,
                        platforms=stub.platforms, transport=t)
        if page is None:
            continue
        for row in page_to_rows(page):
            if notable_only and not row["is_notable"]:
                continue
            yield row


def export_jsonl(rows: Iterable[Dict[str, Any]], path: str) -> int:
    """Write *rows* to a JSON Lines file at *path*. Returns the row count.

    Example::

        from pytcrf import dataset
        rows = dataset.iter_page_rows(platforms=["Genesis"], per_platform_limit=1)
        n = dataset.export_jsonl(rows, "tcrf_pages.jsonl")
    """
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def build_pages_dataset(out_path: str, *,
                        platforms: Optional[List[str]] = None,
                        per_platform_limit: Optional[int] = None,
                        notable_only: bool = False,
                        transport: Optional[Transport] = None) -> int:
    """Crawl the games tree and write the ``pages`` JSONL dataset. Returns rows.

    Convenience wrapper over :func:`iter_page_rows` + :func:`export_jsonl`.
    Validate on a small sample first::

        from pytcrf import dataset
        dataset.build_pages_dataset("tcrf_pages.jsonl",
                                    platforms=["Genesis"], per_platform_limit=3)
    """
    rows = iter_page_rows(platforms=platforms,
                          per_platform_limit=per_platform_limit,
                          notable_only=notable_only, transport=transport)
    return export_jsonl(rows, out_path)


__all__ = ["page_to_rows", "iter_page_rows", "export_jsonl",
           "build_pages_dataset", "load_sections"]
