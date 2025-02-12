"""Run every solution."""

import subprocess
from collections.abc import Mapping, MutableMapping
from pathlib import Path
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
type Stats = tuple[Seconds, Kilobytes, Notes]


def measure_execution_time(dirpath: Path, ext: RunnerFunc) -> Stats:
    try:
        kilobytes, seconds, output = ext(dirpath)
        if output.strip() != "answer":
            return "", "", "Different answer"
    except subprocess.CalledProcessError as e:
        return "", "", f"Error ({e.returncode})"
    return f"{seconds:.2f}", f"{kilobytes}", ""


def from_table(table: str) -> dict[Run, Stats]:
    results: dict[Run, Stats] = {}
    for line in table.split("\n")[6:]:
        if not line:
            break
        day, lang, person, seconds, kb, notes = line[1:-1].split(" | ")
        results[(day.strip(), lang.strip(), person.strip())] = (
            seconds[:-4].strip(),
            kb[:-3].strip(),
            notes.strip(),
        )
    return results


def to_table(results: Mapping[Run, Stats]) -> str:
    table = "\n\n## Stats\n\n"
    table += "| day | language | who | time | mem | notes |\n"
    table += "| --- | --- | --- | --- | --- | --- |\n"
    for (day, language, person), (seconds, kilobytes, notes) in results.items():
        table += f"| {day} | {language} | {person} | {seconds} sec | {kilobytes} KB | {notes} |\n"
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
    for dirpath, dirnames, filenames in path.walk(top_down=True):
        if ".optout" in filenames:
            continue
        # ToDo Is there a better way to traverse the directories alphabetically?
        dirnames.sort()
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            day: Day = dirpath.parts[0][4:]
            if dirpath.parts and len(dirpath.parts) == 2:
                for name, runner in RUNTIMES.items():
                    directory = dirpath.parts[1]
                    language: Language = directory[0 : directory.find("_")]
                    person: Person = directory[directory.find("_") + 1 :]
                    if language == name:
                        results[(day, language, person)] = measure_execution_time(dirpath, runner)

    write_results(results)


if __name__ == "__main__":
    main()
