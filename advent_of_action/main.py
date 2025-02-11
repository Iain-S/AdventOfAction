"""Run every solution."""

import subprocess
import time
from functools import partial
from pathlib import Path
from typing import Final, Mapping
from collections.abc import Callable

RunnerFunc = Callable[[Path], str]

SUBPROCESS_RUN: Final[Callable] = partial(
    subprocess.run, capture_output=True, timeout=60, text=True
)


def execute_command(command: list[str|Path]) -> str:
    print("Running", command)
    return SUBPROCESS_RUN(command).stdout


def run_python(dirpath: Path) -> str:
    """Run a Python solution."""
    return execute_command(
        ["python", dirpath / "solution.py"]
    )


def run_racket(dirpath: Path) -> str:
    """Run a Racket solution."""
    return execute_command(
        ["racket", dirpath / "solution.rkt"]
    )


def run_rust(dirpath: Path) -> str:
    return execute_command(
        ["cargo", "run", "--manifest-path", dirpath / "Cargo.toml"]
    )

def run_fsharp(dirpath: Path) -> str:
    return execute_command(
        ["dotnet", "fsi", dirpath / "solution.fsx"]
    )

def run_ocaml(dirpath: Path) -> str:
    return execute_command(
        ["ocaml", dirpath / "solution.ml"]
    )

def run_jupyter(dirpath: Path) -> str:
    return execute_command(
        ["ipython", "-c", f"%run {dirpath / 'solution.ml'}"]
    )

# Languages and their commands
RUNTIMES: Final[dict[str, RunnerFunc]] = {
    "python": run_python,
    "racket": run_racket,
    "rust": run_rust,
    "fsharp": run_fsharp,
    "ocaml": run_ocaml,
    "jupyter": run_jupyter,
}


def measure_execution_time(dirpath: Path, ext: RunnerFunc) -> str:
    # Use the licence as input while testing.
    start = time.time()
    try:
        output = ext(dirpath)
        if output.strip() != "answer":
            return "Wrong answer"
    except subprocess.CalledProcessError as e:
        return f"Error ({e.returncode})"
    return f"{time.time() - start:.0f} sec"


def update_readme(the_results: Mapping[Path, str]) -> None:
    readme_path = "README.md"
    new_content = "\n## Results\n"
    for the_path, time_taken in the_results.items():
        new_content += f"- `{the_path}`: {time_taken}\n"

    with open(readme_path, "a") as f:
        f.write(new_content)


def main() -> None:
    """Run the solutions."""
    results: dict[Path, str] = {}
    path = Path(".")
    # Expecting
    # ├── day_01
    # │   ├── python_person
    # │   │   └── solution.py
    for dirpath, _, filenames in path.walk():
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            if dirpath.parts and len(dirpath.parts) == 2:
                for name, runner in RUNTIMES.items():
                    if dirpath.parts[1].startswith(name):
                        results[dirpath] = measure_execution_time(dirpath, runner)

    update_readme(results)


if __name__ == "__main__":
    main()
