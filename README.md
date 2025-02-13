# Advent Of Action

If you and your friends/colleagues share a repo for AoC, you can use this to run your solutions to each day's problems.
It will time each person's solution and monitor maximum memory usage, saving the results to the README:

| day | language | who | part | time (s) | mem (KB) | notes |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | python | tina | one | 0.00 | 9728 |  |
| 01 | python | tina | two | 0.02 | 9856 |  |

## Using the Action

See also the [AdventOfActionTest](https://github.com/Iain-S/AdventOfActionTest/tree/main) example repo.

The action expects your code to be laid out with this file structure:

```text
README.md
day_01:
    input.gpg
    answers.gpg
    rust_tom:
        Cargo.toml
    python_tim:
        solution.py
    jupyter_tina:
        solution.ipynb
    racket_tod:
        solution.rkt
    ocaml_tiff:
        solution.ml
    fsharp_tara:
        solution.fsx
    python_travis:
        .optout
        solution.py
```

We currently support Python, IPython notebook, OCaml, Rust, Racket, and F# solutions.
Unsupported languages will be ignored.
To see how each language is executed, look in [runners.py](advent_of_action/runners.py).

For each day, provide an input file named `input.gpg` and a solution file named `answers.gpg`.
Provide the encryption/decryption passphrase as the `gpg-passphrase` input.
This means that someone will need to complete the day's challenge and:

1. Write their answers to `answer.txt`, with the part one answer on the first line and the part two answer on the second.
1. Write the problem input to `input.txt`.
1. Encrypt the files with something like `gpg --batch --yes --symmetric --passphrase "your_secret" --output input|answers.gpg input|answers.txt`.

Input and answers are encrypted because the author of advent-of-code has asked that they be kept private.

Each solution should:

1. Expect the last command-line argument to be either `one` or `two` and to return the part-one or part-two solution accordingly.
1. Expect an `input.txt` file in the current working directory, which is the problem input.

For example:

```python
"""solution.py"""
import sys
from pathlib import Path

def main() -> None:
    text = Path("input.txt").read_text()
    match sys.argv[-1]:
        case "one":
            # Part one solution.
            print(len(text))
        case "two":
            # Part two solution.
            print(len(text) * 2)
        case _:
            print("Unknown argument")
```

If you'd like to opt out of having your code executed, add an `.optout` file to your directory for that day.

The results of running each solution will be written to a table in the README.
You will need to add an extra workflow step to push and commit in order to save that change (see below).

If there are previous results in the README, those solutions will not be re-executed.
To force a re-run, you can delete those lines from the results table in the README.

```yaml
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}
      - name: Run the action
        uses: Iain-S/AdventOfAction@0.1.5
        with:
          # The directory in which you keep the day_xx directories.
          working-directory: ./

          # The passphrase for input.gpg and answers.gpg files.
          # Probably best to store in a repo secret.
          gpg-passphrase: {{ secrets.YOUR_SECRET }}

          # To be passed to the setup-python action.
          python-version: "3.13"

          # To be passed to the setup-dotnet action or -1 to disable.
          dotnet-version: 8

          # To be passed to the setup-racket action or -1 to disable.
          racket-version: -1

          # To be passed to the setup-rust-toolchain action or -1 to disable.
          rust-version: 1.83

          # To be passed to the setup-ocaml action or -1 to disable.
          ocaml-version: -1
      - name: Commit results
        shell: bash
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions@github.com"
          git add README.md
          git commit -m "Update README with results" || echo "No changes to commit"
          git push
```

## Developing the Action

1. Install Poetry.
1. Install Pre-commit.
1. Install Advent of Action, with `poetry install`.
1. Install the pre-commit hooks with `pre-commit install --install-hooks`.
1. Run the unit tests with `cd tests/ && poetry run python test_main.py`.
