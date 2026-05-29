"""List every platform The Cutting Room Floor organises games by.

    python examples/01_list_platforms.py
"""
import pytcrf


def main() -> None:
    platforms = pytcrf.list_platforms()
    print(f"{len(platforms)} platforms")
    for p in platforms[:30]:
        print(" ", p)
    if len(platforms) > 30:
        print(f"  … and {len(platforms) - 30} more")


if __name__ == "__main__":
    main()
