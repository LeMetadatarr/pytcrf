"""Dataset row flattening + JSONL export (offline via fixtures)."""
import json
import os

from pytcrf import dataset
from pytcrf.models import GamePage

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _page():
    with open(os.path.join(FIX, "parse_sonic.json"), encoding="utf-8") as fh:
        parse = json.load(fh)["parse"]
    page = GamePage.from_parse(parse, platforms=["Genesis"])
    # attach fake text to the first couple sections
    for s in page.sections[:2]:
        s.text = "documented cut content for " + s.line
    return page


def test_page_to_rows_shape():
    rows = dataset.page_to_rows(_page())
    assert rows
    r = rows[0]
    assert set(r) >= {"game", "platform", "section", "text", "is_notable", "url"}
    assert r["game"] == "Sonic the Hedgehog (Genesis)"
    assert r["platform"] == "Genesis"
    # one row per section (single platform)
    assert len(rows) == len(_page().sections)


def test_page_to_rows_multi_platform():
    page = _page()
    page.platforms = ["Genesis", "32X"]
    rows = dataset.page_to_rows(page)
    assert len(rows) == 2 * len(page.sections)
    assert {r["platform"] for r in rows} == {"Genesis", "32X"}


def test_export_jsonl(tmp_path):
    rows = dataset.page_to_rows(_page())
    out = str(tmp_path / "pages.jsonl")
    n = dataset.export_jsonl(rows, out)
    assert n == len(rows)
    lines = [json.loads(l) for l in open(out, encoding="utf-8")]
    assert len(lines) == n
    assert all("game" in r and "section" in r for r in lines)


def test_iter_page_rows_notable_only(monkeypatch):
    page = _page()
    monkeypatch.setattr(dataset, "iter_games",
                        lambda **k: iter([page]))
    monkeypatch.setattr(dataset, "get_game",
                        lambda title, **k: page)
    rows = list(dataset.iter_page_rows(notable_only=True))
    assert rows
    assert all(r["is_notable"] for r in rows)
