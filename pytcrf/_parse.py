"""HTML/wikitext parsers for tcrf.net API payloads.

The MediaWiki API returns structured JSON, but ``action=parse&prop=text``
returns rendered **HTML** for a section, and the platform of a game is encoded
in the page's ``{{Game}}`` infobox wikitext. These parsers turn those into plain
text / platform lists and are independent of how the bytes were fetched (see
:mod:`pytcrf.transport`).
"""
from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup

from pytcrf._clean import clean_text

# Rows the rendered HTML carries that are noise for a text corpus.
_DROP_SELECTORS = ("style", "script", "table.toc", "div.toc", "sup.reference")

# {{Game ... |platform=X / |console=X / |system=X ...}} — TCRF's game infobox
# carries the platform in one of a few parameter names, sometimes pipe-joined.
_INFOBOX_PARAM_RE = re.compile(
    r"\|\s*(?:platform|console|system|format)\s*=\s*([^\n|}]+)", re.IGNORECASE)


def section_html_to_text(html: str) -> str:
    """Extract clean plain text from a rendered section HTML fragment."""
    soup = BeautifulSoup(html or "", "html.parser")
    for sel in _DROP_SELECTORS:
        for node in soup.select(sel):
            node.decompose()
    return clean_text(soup.get_text(" ", strip=True))


def platforms_from_wikitext(wikitext: str) -> List[str]:
    """Best-effort platform list from a game page's infobox wikitext.

    Reads ``|platform=`` / ``|console=`` / ``|system=`` parameters from the
    ``{{Game}}`` infobox, splitting on common separators and stripping wiki
    link/markup. Returns ``[]`` when nothing is found (the category tree remains
    the authoritative platform source — see :mod:`pytcrf.games`).
    """
    if not wikitext:
        return []
    found: List[str] = []
    for raw in _INFOBOX_PARAM_RE.findall(wikitext):
        for part in re.split(r"\s*(?:,|/|;|\band\b)\s*", raw):
            name = _strip_markup(part)
            if name and name.lower() not in (p.lower() for p in found):
                found.append(name)
    return found


def _strip_markup(text: str) -> str:
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)  # [[a|b]] -> b
    text = re.sub(r"\{\{[^}]*\}\}", "", text)                       # drop templates
    text = re.sub(r"'{2,}", "", text)                              # bold/italic
    text = re.sub(r"<[^>]+>", "", text)                           # stray html
    return text.strip(" \t'\"")


__all__ = ["section_html_to_text", "platforms_from_wikitext"]
