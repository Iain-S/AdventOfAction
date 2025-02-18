"""A sample solution that reads input.txt."""

import sys
from pathlib import Path

import jsonschema_rs  # noqa  # type: ignore


def main() -> None:
    """Run the solution."""
    text = Path("input.txt").read_text().splitlines()
    match sys.argv[-1]:
        case "one":
            print(text[0].lower())
        case "two":
            print(text[1].lower())
        case _:
            print("Unknown argument")


if __name__ == "__main__":
    main()
