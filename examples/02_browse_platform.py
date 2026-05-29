"""Browse game pages on a platform (cheap stubs — no sections fetched).

    python examples/02_browse_platform.py [PLATFORM]
"""
import sys

import pytcrf


def main() -> None:
    platform = sys.argv[1] if len(sys.argv) > 1 else "Genesis"
    print(f"Games on {platform!r} (first 10):")
    for g in pytcrf.iter_games(platforms=[platform], per_platform_limit=10):
        print(f"  {g.title}  (pageid={g.pageid})")


if __name__ == "__main__":
    main()
