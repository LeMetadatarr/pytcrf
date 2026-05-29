"""Text normalisation helpers shared across pytcrf.

Small, dependency-light string utilities used when turning rendered section HTML
and category titles into clean corpus text. Kept separate from :mod:`_parse`
(which needs BeautifulSoup) so they stay trivially testable.
"""
from __future__ import annotations

import re

# The MediaWiki "[edit]" affordance leaks into rendered section HTML text.
_EDIT_RE = re.compile(r"\s*\[\s*edit\s*\]\s*", re.IGNORECASE)
_WS_RE = re.compile(r"[ \t ]+")
_BLANKLINES_RE = re.compile(r"\n{3,}")
# "Sega Genesis games" / "NES games" -> "Sega Genesis" / "NES"
_PLATFORM_SUFFIX_RE = re.compile(r"\s+games$", re.IGNORECASE)
_CATEGORY_PREFIX_RE = re.compile(r"^Category:", re.IGNORECASE)


def clean_text(text: str) -> str:
    """Collapse whitespace and strip MediaWiki ``[edit]`` markers from text."""
    if not text:
        return ""
    text = _EDIT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = _BLANKLINES_RE.sub("\n\n", text)
    return text.strip()


def platform_from_category(title: str) -> str:
    """Turn a platform category title into a bare platform name.

    ``"Category:Genesis games"`` → ``"Genesis"``; ``"NES games"`` → ``"NES"``.
    """
    title = _CATEGORY_PREFIX_RE.sub("", title).strip()
    return _PLATFORM_SUFFIX_RE.sub("", title).strip()


def strip_category_prefix(title: str) -> str:
    """``"Category:Games"`` → ``"Games"`` (leaves non-category titles alone)."""
    return _CATEGORY_PREFIX_RE.sub("", title).strip()


__all__ = ["clean_text", "platform_from_category", "strip_category_prefix"]
