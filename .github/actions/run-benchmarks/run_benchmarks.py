"""Run every solution."""

import subprocess
import time
from pathlib import Path
from typing import Final, Mapping
from collections.abc import Callable

RunnerFunc = Callable[[Path], str]


def run_python(dirpath: Path) -> str:
    """Run a Python solution."""
    command = ["python", dirpath / "solution.py"]
    print("Running", command)
    completed_process = subprocess.run(command)
    return completed_process.stdout.decode("utf-8")


def run_racket(dirpath: Path) -> str:
    """Run a Racket solution."""
    command = ["racket", dirpath / "solution.rkt"]
    print("Running", command)
    completed_process = subprocess.run(command)
    return completed_process.stdout.decode("utf-8")


# Languages and their commands
RUNTIMES: Final[dict[str, RunnerFunc]] = {
    "python": run_python,
    "racket": run_racket,
}


def measure_execution_time(dirpath: Path, ext: RunnerFunc) -> str:
    # Use the licence as input while testing.
    start = time.time()
    try:
        output = ext(dirpath)
        if output != "answer":
            return "Error"
    except subprocess.CalledProcessError as e:
        return f"Error ({e.returncode})"
    return f"{time.time() - start:.3f} sec"


def update_readme(the_results: Mapping[Path, str]) -> None:
    readme_path = "README.md"
    new_content = "\n## Benchmark Results\n"
    for the_path, time_taken in the_results.items():
        new_content += f"- `{the_path}`: {time_taken}\n"

    with open(readme_path, "a") as f:
        f.write(new_content)


def main() -> None:
    """Run the benchmarks."""
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
