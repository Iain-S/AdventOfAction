"""Run every solution."""

import subprocess
from pathlib import Path
from typing import Final, Mapping
from collections.abc import Callable

type Triple = tuple[int, float, str]
type RunnerFunc = Callable[[Path], Triple]

def execute_command(command: list[str|Path]) -> Triple:
    # Here rather than globally as it's easier to patch.
    print("Running", command)
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%M,%S,%U"] + command,
        capture_output=True, timeout=60, text=True, check=True
    )
    # todo
    # kilobytes, sys_seconds, user_seconds = result.stderr.split("\n")[-1].split(",")
    kilobytes, sys_seconds, user_seconds = result.stderr.split(",")
    return int(kilobytes), float(sys_seconds)+float(user_seconds), result.stdout


def run_python(dirpath: Path) -> Triple:
    """Run a Python solution."""
    return execute_command(
        ["python", dirpath / "solution.py"]
    )


def run_racket(dirpath: Path) -> Triple:
    """Run a Racket solution."""
    return execute_command(
        ["racket", dirpath / "solution.rkt"]
    )


def run_rust(dirpath: Path) -> Triple:
    return execute_command(
        ["cargo", "run", "--quiet", "--manifest-path", dirpath / "Cargo.toml"]
    )

def run_fsharp(dirpath: Path) -> Triple:
    return execute_command(
        ["dotnet", "fsi", dirpath / "solution.fsx"]
    )

def run_ocaml(dirpath: Path) -> Triple:
    return execute_command(
        ["ocaml", dirpath / "solution.ml"]
    )

def run_jupyter(dirpath: Path) -> Triple:
    return execute_command(
        ["ipython", "-c", f"%run {dirpath / 'solution.ipynb'}"]
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
    try:
        kilobytes, seconds, output = ext(dirpath)
        if output.strip() != "answer":
            return "Wrong answer"
    except subprocess.CalledProcessError as e:
        return f"Error ({e.returncode})"
    return f"{seconds:.2f} sec, {kilobytes} KB"


def update_readme(the_results: Mapping[Path, str]) -> None:
    readme_path = "README.md"
    new_content = "\n## Results\n\n"
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
    for dirpath, dirnames, filenames in path.walk(top_down=True):
        # ToDo Is there a better way to traverse the directories alphabetically?
        if ".optout" in filenames:
            continue
        dirnames.sort()
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            if dirpath.parts and len(dirpath.parts) == 2:
                for name, runner in RUNTIMES.items():
                    if dirpath.parts[1].startswith(name):
                        results[dirpath] = measure_execution_time(dirpath, runner)

    update_readme(results)


if __name__ == "__main__":
    main()
