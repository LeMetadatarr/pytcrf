"""Public surface is importable and stable."""
import pytcrf


def test_version():
    assert isinstance(pytcrf.__version__, str)
    assert pytcrf.__version__.startswith("0.0.1")


def test_exports():
    for name in [
        "GamePage", "Section", "CategoryMember", "page_url",
        "TCRF", "Transport", "ScraperBlocked",
        "get_game", "get_section_text", "load_sections",
        "iter_games", "iter_category_members", "iter_platform_categories",
        "iter_platform_games", "list_platforms",
        "GAMES_CATEGORY", "GAMES_BY_PLATFORM",
    ]:
        assert hasattr(pytcrf, name), name


def test_dataset_and_ids_importable():
    from pytcrf import dataset, ids
    assert hasattr(dataset, "export_jsonl")
    assert hasattr(dataset, "iter_page_rows")
    assert hasattr(ids, "game_to_extra")
    assert hasattr(ids, "canonical_id")
