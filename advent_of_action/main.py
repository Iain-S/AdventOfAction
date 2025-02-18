"""Run every solution."""

import os
from collections.abc import Generator, Mapping, MutableMapping
from contextlib import contextmanager
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, run
from typing import Final

from advent_of_action import runners
from advent_of_action.runners import Commands, Part, execute_command

# Languages and their commands
RUNTIMES: Final = {
    "python": runners.PYTHON,
    "racket": runners.RACKET,
    "rust": runners.RUST,
    "fsharp": runners.FSHARP,
    "ocaml": runners.OCAML,
    "jupyter": runners.JUPYTER,
}

type Day = str
type Language = str
type Person = str
type Seconds = str
type Kilobytes = str
type Notes = str
type Run = tuple[Day, Language, Person]
type Stat = tuple[Seconds, Kilobytes, Notes]
type Stats = tuple[Stat, Stat]

# Prevent Ruff from simplifying Generator[None, None, None] to Generator[None],
# which Pyre treats as Generator[None, Any, None].
type Nothing = None | None


def measure_execution_time(answers: tuple[str, str], comm: Commands) -> Stats:
    """Measure the execution time of a solution."""

    def inner(part: Part, answer: str | None, command: list[str | Path]) -> Stat:
        """Use the runner to measure the execution time of one part."""
        try:
            if answer is not None:
                kilobytes, seconds, output = execute_command(command + [part.value])
                if output != answer:
                    print(f"Incorrect answer for part {part}: {output}")
                    return "", "", "Different answer"
                else:
                    return f"{seconds:.2f}", f"{kilobytes}", ""
            else:
                # Ignore empty lists.
                if command:
                    execute_command(command, timeout=60.0)
                return "", "", "Done"

        except CalledProcessError as e:
            # Print all but the last line, which will be the timings.
            print("".join(e.stderr.splitlines()[:-1]))
            return "", "", f"Error ({e.returncode})"
        except TimeoutExpired as e:
            print(f"Command timed out after {e.timeout:.0f} seconds")
            return "", "", "Timeout"

    return (
        inner(Part.SETUP, None, comm.setup),
        inner(Part.ONE, answers[0], comm.run),
        inner(Part.TWO, answers[1], comm.run),
        inner(Part.TEARDOWN, None, comm.teardown),
    )[1:3]


def from_table(table: str) -> dict[Run, Stats]:
    """Extract results from the Markdown ##Stats section."""
    results: dict[Run, Stats] = {}
    part_one = None
    for line in table.splitlines()[6:]:
        if not line:
            break
        day, lang, person, part, seconds, kb, notes = line[1:-1].split(" | ")
        if part == Part.ONE:
            part_one = (seconds.strip(), kb.strip(), notes.strip())
        elif part == Part.TWO:
            assert part_one is not None
            results[(day.strip(), lang.strip(), person.strip())] = (
                part_one,
                (seconds.strip(), kb.strip(), notes.strip()),
            )
        else:
            raise ValueError(f"Unknown part {part}")

    return results


def to_table(results: Mapping[Run, Stats]) -> str:
    """Convert results to a Markdown table."""
    table = "\n\n## Stats\n\n"
    table += "| day | language | who | part | time (s) | mem (KB) | notes |\n"
    table += "| --- | --- | --- | --- | --- | --- | --- |\n"
    for the_run, stats in results.items():
        day, language, person = the_run
        for (seconds, kilobytes, notes), part in zip(stats, (Part.ONE, Part.TWO), strict=False):
            table += f"| {day} | {language} | {person} | {part} | {seconds} | {kilobytes} | {notes} |\n"
    return table


def write_results(the_results: Mapping[Run, Stats]) -> None:
    """Write results to the README."""
    readme = Path("README.md")
    old_content = readme.read_text()
    section_begins = old_content.find("\n\n## Stats")
    if section_begins > -1:
        section_ends = old_content.find("\n\n##", section_begins + 1)
        section = old_content[section_begins:section_ends] if section_ends else old_content[section_begins:]
        old_dict = from_table(section)
        the_results = {**old_dict, **the_results}
        if section_ends > -1:
            new_content = old_content[:section_begins] + to_table(the_results) + old_content[section_ends:]
        else:
            new_content = old_content[:section_begins] + to_table(the_results)
    else:
        new_content = old_content + to_table(the_results)
    readme.write_text(new_content)


@contextmanager
def chdir(new_path: Path) -> Generator[None, Nothing, Nothing]:
    """Context manager for changing the current working directory."""
    saved_path = Path.cwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(saved_path)


def main() -> None:
    """Run the solutions."""
    results: MutableMapping[Run, Stats] = {}

    # Get the previous results.
    # todo Refactor this into a function.
    readme = Path("README.md")
    old_content = readme.read_text()
    section_begins = old_content.find("\n\n## Stats")
    if section_begins > -1:
        section_ends = old_content.find("\n\n##", section_begins + 1)
        section = old_content[section_begins:section_ends] if section_ends else old_content[section_begins:]
        results = from_table(section)

    # Expecting
    # ├── day_01
    # │   ├── python_person
    # │   │   └── solution.py
    for day_dir in sorted(list(Path(".").glob("day_*"))):
        day: Day = day_dir.parts[0][4:]
        answers = get_answers(day_dir)

        for solution_dir in sorted(list(day_dir.glob("*_*"))):
            if ".optout" in set([x.name for x in solution_dir.iterdir() if x.is_file()]):
                continue
            directory = solution_dir.parts[1]
            language, person = directory.split("_", maxsplit=1)
            if (day, language, person) not in results and language in RUNTIMES:
                with chdir(solution_dir):
                    make_input_file()
                    results[(day, language, person)] = measure_execution_time(answers, RUNTIMES[language])

    write_results(results)


def make_input_file() -> None:
    """Decrypt the input file."""
    if (passphrase := os.getenv("GPG_PASS")) is None:
        raise ValueError("GPG_PASS environment variable not set.")

    run(
        [
            "gpg",
            "--batch",
            "--yes",
            "--passphrase",
            passphrase,
            "--decrypt",
            "--output",
            # Scripts expect input.txt to be in the CWD.
            Path("input.txt"),
            "../input.gpg",
        ],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )


def get_answers(dirpath: Path) -> tuple[str, str]:
    """Get today's answers from the encrypted file."""
    if (passphrase := os.getenv("GPG_PASS")) is None:
        raise ValueError("GPG_PASS environment variable not set.")

    run(
        [
            "gpg",
            "--batch",
            "--yes",
            "--passphrase",
            passphrase,
            "--decrypt",
            "--output",
            Path("answers.txt"),
            dirpath / "answers.gpg",
        ],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    lines = Path("answers.txt").read_text().splitlines()
    answers = lines[0], lines[1]
    Path("answers.txt").unlink()
    return answers


if __name__ == "__main__":
    main()  # pragma: no cover
