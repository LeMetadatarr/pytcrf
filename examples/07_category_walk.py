"""Walk an arbitrary category — e.g. unlicensed or unreleased games.

    python examples/07_category_walk.py ["Category:Unlicensed games"] [LIMIT]
"""
import sys

import pytcrf


def main() -> None:
    category = sys.argv[1] if len(sys.argv) > 1 else "Category:Unlicensed games"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    print(f"Pages in {category!r} (up to {limit}):")
    for m in pytcrf.iter_category_members(category, member_type="page", limit=limit):
        print(f"  {m.title}")


if __name__ == "__main__":
    main()
