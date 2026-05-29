"""Live smoke test — hits tcrf.net. Run with ``pytest -m live``.

Skipped by default (the suite is offline). Validates the real interstitial
bypass and section parse end to end on a stable, well-documented page.
"""
import pytest

import pytcrf

pytestmark = pytest.mark.live


def test_live_get_game_sections():
    game = pytcrf.get_game("Sonic the Hedgehog (Genesis)")
    assert game is not None
    assert game.title == "Sonic the Hedgehog (Genesis)"
    assert game.sections, "section structure should be parsed"
    # the page is famous for its debug/unused content
    assert game.notable_sections
    assert "Genesis" in game.platforms


def test_live_list_platforms():
    plats = pytcrf.list_platforms()
    assert len(plats) > 50
    assert any("Genesis" in p for p in plats)
