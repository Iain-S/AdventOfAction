import sys
from pathlib import Path


def main() -> None:
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
