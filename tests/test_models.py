"""Model construction, URL building and ids conversion (no network)."""
import json
import os

from pytcrf.ids import canonical_id, game_to_extra
from pytcrf.models import CategoryMember, GamePage, page_url

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read_json(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


def test_page_url():
    assert page_url("Sonic the Hedgehog (Genesis)") == \
        "https://tcrf.net/Sonic_the_Hedgehog_(Genesis)"


def test_category_member_from_api():
    data = _read_json("categorymembers_genesis.json")
    members = [CategoryMember.from_api(n)
               for n in data["query"]["categorymembers"]]
    assert members
    assert all(m.title for m in members)
    # ns 0 pages here, not subcats
    assert any(not m.is_subcategory for m in members)


def test_platform_categories_are_subcats():
    data = _read_json("platform_categories.json")
    members = [CategoryMember.from_api(n)
               for n in data["query"]["categorymembers"]]
    assert members
    assert all(m.is_subcategory for m in members)


def test_game_to_extra_anchor_and_payload():
    parse = _read_json("parse_sonic.json")["parse"]
    page = GamePage.from_parse(parse, platforms=["Genesis"])
    extra = game_to_extra(page)
    # canonical anchor
    assert extra["tcrf_title"] == "Sonic the Hedgehog (Genesis)"
    assert canonical_id(page) == "Sonic the Hedgehog (Genesis)"
    assert extra["tcrf_url"].startswith("https://tcrf.net/")
    assert extra["tcrf_pageid"] == "1583"
    assert json.loads(extra["tcrf_platforms"]) == ["Genesis"]
    # notable sections serialised as JSON array of strings
    notable = json.loads(extra["tcrf_notable_sections"])
    assert isinstance(notable, list) and notable


def test_gamepage_to_dict_roundtrip_serialisable():
    parse = _read_json("parse_sonic.json")["parse"]
    page = GamePage.from_parse(parse, platforms=["Genesis"])
    d = page.to_dict()
    json.dumps(d)  # must be JSON-serialisable
    assert d["title"] == page.title
    assert len(d["sections"]) == len(page.sections)


def test_gamepage_from_parse_empty_node():
    page = GamePage.from_parse({})
    assert page.title == ""
    assert page.pageid is None
    assert page.platforms == []
    assert page.sections == []
    assert page.wikitext is None


def test_category_member_from_api_missing_pageid():
    member = CategoryMember.from_api({"title": "Category:Orphaned"})
    assert member.pageid is None
    assert member.ns == 0
    assert not member.is_subcategory


def test_game_to_extra_minimal_page_has_no_optional_keys():
    page = GamePage(title="Untitled Prototype")
    extra = game_to_extra(page)
    assert extra["tcrf_title"] == "Untitled Prototype"
    assert "tcrf_pageid" not in extra
    assert "tcrf_platforms" not in extra
    assert "tcrf_sections" not in extra
    assert "tcrf_notable_sections" not in extra
