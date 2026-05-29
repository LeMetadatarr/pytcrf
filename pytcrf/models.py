"""Typed dataclass models for pytcrf.

The Cutting Room Floor documents the unused, cut, regional and debug content of
individual games. pytcrf models that as:

- :class:`Section` — one heading in a game article (level, line, anchor,
  optional plain text). The section tree *is* the structure of a TCRF page:
  ``Unused Graphics``, ``Debug Mode``, ``Regional Differences``,
  ``Revisional Differences``, etc.
- :class:`GamePage` — a game article: its canonical ``tcrf_title`` (the anchor
  identity), page id, detected platform(s), the flat section list and the raw
  wikitext when fetched.
- :class:`CategoryMember` — a lightweight ``(title, pageid, ns)`` row from a
  ``categorymembers`` enumeration of the ``Category:Games`` tree.

Shared interface: ``url`` (canonical page), ``to_dict()`` (JSON-serialisable),
and ``from_api()`` builders that consume the raw MediaWiki JSON nodes.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import quote

BASE = "https://tcrf.net"

# Heading lines that flag a section as cut/unused/regional/debug content — the
# part of a TCRF page that is actually preservation-relevant.
NOTABLE_SECTION_HINTS = (
    "unused", "cut", "debug", "regional", "revision", "prototype", "beta",
    "leftover", "hidden", "removed", "development", "early", "placeholder",
    "test", "oddit", "anti-piracy", "easter egg",
)


def page_url(title: str) -> str:
    """Canonical tcrf.net article URL for a page *title*."""
    return f"{BASE}/{quote(title.replace(' ', '_'), safe='/():,!')}"


@dataclass
class Section:
    """One heading within a game article.

    ``index`` is the MediaWiki section index (usable as ``parse&section=...``);
    ``level`` is the heading depth (``2`` == ``==H2==``); ``line`` is the
    rendered heading text; ``anchor`` is its fragment id; ``text`` is the plain
    extracted body when the section has been fetched.
    """

    index: str
    level: int
    line: str
    anchor: str
    text: Optional[str] = None

    @classmethod
    def from_api(cls, node: dict) -> "Section":
        return cls(
            index=str(node.get("index") or ""),
            level=int(node.get("level") or node.get("toclevel") or 0),
            line=(node.get("line") or "").strip(),
            anchor=node.get("anchor") or "",
        )

    @property
    def is_notable(self) -> bool:
        """True when the heading looks like cut/unused/regional/debug content."""
        low = self.line.lower()
        return any(h in low for h in NOTABLE_SECTION_HINTS)

    def to_dict(self) -> Dict[str, Any]:
        d = {k: v for k, v in dataclasses.asdict(self).items() if v is not None}
        d["is_notable"] = self.is_notable
        return d


@dataclass
class CategoryMember:
    """A page or subcategory row from a ``categorymembers`` enumeration."""

    title: str
    pageid: Optional[int] = None
    ns: int = 0

    @classmethod
    def from_api(cls, node: dict) -> "CategoryMember":
        return cls(title=node.get("title") or "",
                   pageid=node.get("pageid"),
                   ns=int(node.get("ns") or 0))

    @property
    def is_subcategory(self) -> bool:
        return self.ns == 14

    @property
    def url(self) -> str:
        return page_url(self.title)

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "pageid": self.pageid, "ns": self.ns,
                "is_subcategory": self.is_subcategory, "url": self.url}


@dataclass
class GamePage:
    """A TCRF game article and its section structure.

    The canonical identity is :attr:`title` (the ``tcrf_title`` anchor). Obtain
    via :func:`pytcrf.get_game` / :func:`pytcrf.iter_games`.
    """

    title: str
    pageid: Optional[int] = None
    platforms: List[str] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)
    wikitext: Optional[str] = None

    @classmethod
    def from_parse(cls, node: dict, *, platforms: Optional[List[str]] = None) -> "GamePage":
        """Build from an ``action=parse`` result node."""
        wt = None
        raw_wt = node.get("wikitext")
        if isinstance(raw_wt, dict):
            wt = raw_wt.get("*")
        elif isinstance(raw_wt, str):
            wt = raw_wt
        return cls(
            title=node.get("title") or "",
            pageid=node.get("pageid"),
            platforms=list(platforms or []),
            sections=[Section.from_api(s) for s in (node.get("sections") or [])],
            wikitext=wt,
        )

    @property
    def url(self) -> str:
        return page_url(self.title)

    @property
    def notable_sections(self) -> List[Section]:
        """Sections whose heading flags cut/unused/regional/debug content."""
        return [s for s in self.sections if s.is_notable]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "pageid": self.pageid,
            "url": self.url,
            "platforms": self.platforms,
            "sections": [s.to_dict() for s in self.sections],
            "wikitext": self.wikitext,
        }


__all__ = ["Section", "CategoryMember", "GamePage", "page_url",
           "NOTABLE_SECTION_HINTS", "BASE"]
