"""Text/category normalisation helpers (no network)."""
from pytcrf._clean import (
    clean_text,
    platform_from_category,
    strip_category_prefix,
)


def test_clean_text_strips_edit_and_collapses_ws():
    raw = "Debug Mode [ edit ]   Another   well-known    code."
    out = clean_text(raw)
    assert "[ edit ]" not in out and "[edit]" not in out
    # runs of inline whitespace collapse to a single space
    assert "  " not in out
    assert out == "Debug Mode Another well-known code."


def test_clean_text_collapses_blank_lines():
    out = clean_text("para one\n\n\n\n\npara two")
    # 3+ blank lines collapse to a single paragraph break, no more
    assert "\n\n\n" not in out
    assert out == "para one\n\npara two"


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text(None) == ""  # type: ignore[arg-type]


def test_platform_from_category():
    assert platform_from_category("Category:Genesis games") == "Genesis"
    assert platform_from_category("NES games") == "NES"
    assert platform_from_category("Category:Arcade games") == "Arcade"


def test_strip_category_prefix():
    assert strip_category_prefix("Category:Games") == "Games"
    assert strip_category_prefix("Sonic the Hedgehog (Genesis)") == \
        "Sonic the Hedgehog (Genesis)"
