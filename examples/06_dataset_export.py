"""Export a (game, platform, section, text) JSONL dataset — small sample.

    python examples/06_dataset_export.py [PLATFORM] [N_GAMES] [OUT.jsonl]
"""
import sys

from pytcrf import dataset


def main() -> None:
    platform = sys.argv[1] if len(sys.argv) > 1 else "Genesis"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    out = sys.argv[3] if len(sys.argv) > 3 else "tcrf_pages.jsonl"

    rows = dataset.build_pages_dataset(
        out, platforms=[platform], per_platform_limit=n, notable_only=True)
    print(f"wrote {rows} rows to {out}  (platform={platform}, {n} games, notable-only)")


if __name__ == "__main__":
    main()
