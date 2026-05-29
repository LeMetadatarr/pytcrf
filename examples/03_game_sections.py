"""Fetch one game's section structure — its cut/unused/debug content map.

    python examples/03_game_sections.py ["Game Title"]
"""
import sys

import pytcrf


def main() -> None:
    title = sys.argv[1] if len(sys.argv) > 1 else "Sonic the Hedgehog (Genesis)"
    game = pytcrf.get_game(title)
    if game is None:
        print(f"No such page: {title!r}")
        return
    print(f"{game.title}  —  platforms: {game.platforms}")
    print("\nSection tree:")
    for s in game.sections:
        flag = "  *" if s.is_notable else "   "
        print(f"{flag} {'  ' * (s.level - 2)}{s.line}")
    print(f"\n{len(game.notable_sections)} notable (cut/unused/regional/debug) "
          "sections marked with *")


if __name__ == "__main__":
    main()
