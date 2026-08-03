"""Orchestration/edge-case tests for pytcrf.games (no network).

These exercise control flow — pagination continuation, missing-page handling,
platform merging across categories — with a minimal fake transport. Parsing
of real HTML/wikitext bodies is covered separately in ``test_parse.py``
against recorded fixtures.
"""
from pytcrf.games import (
    get_game,
    get_section_text,
    iter_category_members,
    iter_games,
    load_sections,
)
from pytcrf.models import Section


class FakeTransport:
    """Replays a queue of canned ``api()`` responses, recording the calls made."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def api(self, params):
        self.calls.append(params)
        return self._responses.pop(0)


def test_iter_category_members_follows_continuation():
    """A ``continue`` block in the response must trigger a second api() call
    whose params are merged with the continuation cursor, and stop once the
    wiki stops returning one."""
    t = FakeTransport([
        {
            "query": {"categorymembers": [
                {"title": "Game A", "pageid": 1, "ns": 0},
                {"title": "Game B", "pageid": 2, "ns": 0},
            ]},
            "continue": {"cmcontinue": "next-page|123", "continue": "-||"},
        },
        {
            "query": {"categorymembers": [
                {"title": "Game C", "pageid": 3, "ns": 0},
            ]},
        },
    ])
    members = list(iter_category_members("Genesis games", transport=t))
    assert [m.title for m in members] == ["Game A", "Game B", "Game C"]
    assert len(t.calls) == 2
    # the continuation cursor from call 1 must be forwarded on call 2
    assert t.calls[1]["cmcontinue"] == "next-page|123"
    # bare category names get the "Category:" namespace prefixed
    assert t.calls[0]["cmtitle"] == "Category:Genesis games"


def test_iter_category_members_respects_limit_across_pages():
    t = FakeTransport([
        {
            "query": {"categorymembers": [
                {"title": "Game A", "pageid": 1, "ns": 0},
                {"title": "Game B", "pageid": 2, "ns": 0},
            ]},
            "continue": {"cmcontinue": "cursor"},
        },
    ])
    members = list(iter_category_members("Category:Genesis games", limit=1,
                                          transport=t))
    assert [m.title for m in members] == ["Game A"]
    # stopped after the limit — never made a second call for more pages
    assert len(t.calls) == 1


def test_get_game_returns_none_for_missing_page():
    t = FakeTransport([{}])  # no "parse" key: the page doesn't exist
    assert get_game("Definitely Not A Real Page", transport=t) is None


def test_load_sections_skips_sections_without_index():
    page_sections = [
        Section(index="", level=2, line="Intro-like stub", anchor="x"),
        Section(index="1", level=2, line="Debug Mode", anchor="Debug_Mode"),
    ]

    class Page:
        title = "Some Game"
        sections = page_sections

    t = FakeTransport([
        {"parse": {"text": {"*": "<p>debug text</p>"}}},
    ])
    load_sections(Page(), transport=t)
    assert page_sections[0].text is None  # untouched, no api() call spent on it
    assert page_sections[1].text == "debug text"
    assert len(t.calls) == 1
    assert t.calls[0]["section"] == "1"


def test_get_section_text_empty_response():
    t = FakeTransport([{"parse": {}}])
    assert get_section_text("Some Game", "3", transport=t) == ""


def test_iter_games_merges_platforms_for_page_in_two_categories():
    t = FakeTransport([
        # Category:Games by platform -> two platform leaf categories
        {"query": {"categorymembers": [
            {"title": "Category:Genesis games", "pageid": 10, "ns": 14},
            {"title": "Category:32X games", "pageid": 11, "ns": 14},
        ]}},
        # Category:Genesis games -> one page
        {"query": {"categorymembers": [
            {"title": "Chaotix", "pageid": 100, "ns": 0},
        ]}},
        # Category:32X games -> the same page again
        {"query": {"categorymembers": [
            {"title": "Chaotix", "pageid": 100, "ns": 0},
        ]}},
    ])
    games = list(iter_games(transport=t))
    assert len(games) == 1
    assert games[0].title == "Chaotix"
    assert set(games[0].platforms) == {"Genesis", "32X"}


def test_iter_games_filters_by_requested_platform_case_insensitively():
    t = FakeTransport([
        {"query": {"categorymembers": [
            {"title": "Category:Genesis games", "pageid": 10, "ns": 14},
            {"title": "Category:SNES games", "pageid": 12, "ns": 14},
        ]}},
        {"query": {"categorymembers": [
            {"title": "Sonic the Hedgehog (Genesis)", "pageid": 1583, "ns": 0},
        ]}},
    ])
    games = list(iter_games(platforms=["genesis"], transport=t))
    assert [g.title for g in games] == ["Sonic the Hedgehog (Genesis)"]
    # the SNES leaf category was never walked for members
    assert len(t.calls) == 2
