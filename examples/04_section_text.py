"""Read the plain text of a game's notable sections.

    python examples/04_section_text.py ["Game Title"]
"""
import sys

import pytcrf


def main() -> None:
    title = sys.argv[1] if len(sys.argv) > 1 else "Sonic the Hedgehog (Genesis)"
    game = pytcrf.get_game(title, with_section_text=True)
    if game is None:
        print(f"No such page: {title!r}")
        return
    print(f"# {game.title}\n")
    for s in game.notable_sections[:5]:
        print(f"## {s.line}")
        body = (s.text or "")[:300]
        print(body + ("…" if s.text and len(s.text) > 300 else ""))
        print()


if __name__ == "__main__":
    main()
