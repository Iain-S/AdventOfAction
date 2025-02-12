"""Run every solution."""

import subprocess
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Final

from . import runners
from .runners import RunnerFunc

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
    return f"{seconds:.2f} sec", f"{kilobytes} KB", ""


def write_results(the_results: Mapping[Run, Stats]) -> None:
    readme_path = "README.md"
    new_content = "\n## Results\n\n"
    new_content += "| day | language | who | time | mem | notes |\n"
    new_content += "| --- | --- | --- | --- | --- | --- |\n"
    for (day, language, person), (seconds, kilobytes, notes) in the_results.items():
        new_content += f"| {day} | {language} | {person} | {seconds} | {kilobytes} | {notes} |\n"

    old_content = ""
    if Path(readme_path).exists():
        with open(readme_path) as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == "## Results":
                    break
                old_content += line
    with open(readme_path, "w") as f:
        f.write(old_content + new_content)


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
