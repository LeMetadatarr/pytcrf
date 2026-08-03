"""Offline parser tests against real tcrf.net API fixtures (no network)."""
import json
import os

from pytcrf._parse import platforms_from_wikitext, section_html_to_text
from pytcrf.models import GamePage, Section

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read_json(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


def test_gamepage_from_parse_sections():
    parse = _read_json("parse_sonic.json")["parse"]
    page = GamePage.from_parse(parse, platforms=["Genesis"])
    assert page.title == "Sonic the Hedgehog (Genesis)"
    assert page.pageid == 1583
    assert len(page.sections) > 10
    assert all(isinstance(s, Section) for s in page.sections)
    # the cut/unused/debug structure is detected
    notable = [s.line for s in page.notable_sections]
    assert any("Debug Mode" == n or "Debug" in n for n in notable)
    assert any("Unused" in n for n in notable)


def test_platforms_from_wikitext_infobox():
    parse = _read_json("parse_sonic.json")["parse"]
    wt = parse["wikitext"]["*"]
    plats = platforms_from_wikitext(wt)
    assert "Genesis" in plats


def test_platforms_from_wikitext_empty():
    assert platforms_from_wikitext("") == []
    assert platforms_from_wikitext("no infobox here") == []


def test_section_html_to_text():
    data = _read_json("section_text_sonic.json")
    html = data["parse"]["text"]["*"]
    text = section_html_to_text(html)
    assert "[edit]" not in text and "[ edit ]" not in text
    assert "Debug Mode" in text
    assert len(text) > 100


def test_section_is_notable_flag():
    assert Section("1", 2, "Unused Graphics", "Unused_Graphics").is_notable
    assert Section("2", 2, "Regional Differences", "x").is_notable
    assert not Section("3", 2, "Sub-Pages", "Sub-Pages").is_notable


def test_section_html_to_text_empty_and_malformed():
    assert section_html_to_text("") == ""
    assert section_html_to_text(None) == ""  # type: ignore[arg-type]
    # unclosed tags must not raise
    assert section_html_to_text("<p>Unused text<div>nested") == "Unused text nested"


def test_section_html_to_text_drops_toc_and_references():
    html = ('<div class="toc">Contents</div>'
            '<p>Debug Mode found <sup class="reference">[1]</sup> here</p>')
    text = section_html_to_text(html)
    assert "Contents" not in text
    assert "[1]" not in text
    assert "Debug Mode found" in text and "here" in text


def test_platforms_from_wikitext_multiple_separators():
    wt = "{{Game\n | platform= [[Genesis]], [[32X]] and [[Sega CD]]\n}}"
    assert platforms_from_wikitext(wt) == ["Genesis", "32X", "Sega CD"]
