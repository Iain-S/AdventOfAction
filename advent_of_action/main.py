"""Run every solution."""

import subprocess
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from subprocess import run
from typing import Final

from advent_of_action import runners
from advent_of_action.runners import RunnerFunc

# Languages and their commands
RUNTIMES: Final[dict[str, RunnerFunc]] = {
    "python": runners.python,
    "racket": runners.racket,
    "rust": runners.rust,
    "fsharp": runners.fsharp,
    "ocaml": runners.ocaml,
    "jupyter": runners.jupyter,
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


def measure_execution_time(answers: tuple[str, str], dirpath: Path, ext: RunnerFunc) -> Stats:
    """Measure the execution time of a solution."""

    def inner(part: str, answer: str) -> Stat:
        try:
            kilobytes, seconds, output = ext(dirpath, part)
            if output.strip() != answer:
                return "", "", "Different answer"
        except subprocess.CalledProcessError as e:
            return "", "", f"Error ({e.returncode})"
        return f"{seconds:.2f}", f"{kilobytes}", ""

    return inner("one", answers[0]), inner("two", answers[1])


def from_table(table: str) -> dict[Run, Stats]:
    results: dict[Run, Stats] = {}
    part_one = None
    for line in table.splitlines()[6:]:
        if not line:
            break
        day, lang, person, part, seconds, kb, notes = line[1:-1].split(" | ")
        if part == "one":
            part_one = (seconds.strip(), kb.strip(), notes.strip())
        elif part == "two":
            assert part_one is not None
            results[(day.strip(), lang.strip(), person.strip())] = (
                part_one,
                (seconds.strip(), kb.strip(), notes.strip()),
            )
        else:
            raise ValueError(f"Unknown part {part}")

    return results


def to_table(results: Mapping[Run, Stats]) -> str:
    table = "\n\n## Stats\n\n"
    table += "| day | language | who | part | time (s) | mem (KB) | notes |\n"
    table += "| --- | --- | --- | --- | --- | --- | --- |\n"
    for the_run, stats in results.items():
        day, language, person = the_run
        for (seconds, kilobytes, notes), part in zip(stats, ("one", "two"), strict=False):
            table += f"| {day} | {language} | {person} | {part} | {seconds} | {kilobytes} | {notes} |\n"
    return table


def write_results(the_results: Mapping[Run, Stats]) -> None:
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


def main() -> None:
    """Run the solutions."""
    results: MutableMapping[Run, Stats] = {}
    path = Path(".")
    # Expecting
    # ├── day_01
    # │   ├── python_person
    # │   │   └── solution.py
    answers = ("", "")  # todo
    for dirpath, dirnames, filenames in path.walk(top_down=True):
        if ".optout" in filenames:
            continue
        # ToDo Is there a better way to traverse the directories alphabetically?
        dirnames.sort()
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            day: Day = dirpath.parts[0][4:]

            if len(dirpath.parts) == 1:
                # Note that we don't patch this run in tests.
                run(
                    [
                        "gpg",
                        "--batch",
                        "--yes",
                        "--passphrase",
                        "yourpassword",
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

                # Scripts expect input to be in the CWD.
                # Note that we don't patch this run in tests.
                run(
                    [
                        "gpg",
                        "--batch",
                        "--yes",
                        "--passphrase",
                        "yourpassword",
                        "--decrypt",
                        "--output",
                        Path("input.txt"),
                        dirpath / "input.gpg",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=10,
                )

            if len(dirpath.parts) == 2:
                directory = dirpath.parts[1]
                for name, runner in RUNTIMES.items():
                    language: Language = directory[0 : directory.find("_")]
                    person: Person = directory[directory.find("_") + 1 :]
                    if language == name:
                        results[(day, language, person)] = measure_execution_time(answers, dirpath, runner)

    write_results(results)


if __name__ == "__main__":
    main()
