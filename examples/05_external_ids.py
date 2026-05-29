"""Convert a game page to a mediavocab ExternalIds.extra dict (tcrf_title anchor).

    python examples/05_external_ids.py ["Game Title"]
"""
import json
import sys

import pytcrf
from pytcrf.ids import canonical_id, game_to_extra


def main() -> None:
    title = sys.argv[1] if len(sys.argv) > 1 else "Sonic the Hedgehog (Genesis)"
    game = pytcrf.get_game(title)
    if game is None:
        print(f"No such page: {title!r}")
        return
    print("canonical id:", canonical_id(game))
    print(json.dumps(game_to_extra(game), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
