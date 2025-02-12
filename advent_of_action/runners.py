import subprocess
from collections.abc import Callable
from pathlib import Path

type Triple = tuple[int, float, str]
type RunnerFunc = Callable[[Path], Triple]


def execute_command(command: list[str | Path]) -> Triple:
    """Execute a command and return the memory usage, time and stdout."""
    print("Running", command)
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%M,%S,%U"] + command, capture_output=True, timeout=60, text=True, check=True
    )
    # todo
    # kilobytes, sys_seconds, user_seconds = result.stderr.split("\n")[-1].split(",")
    kilobytes, sys_seconds, user_seconds = result.stderr.split(",")
    return int(kilobytes), float(sys_seconds) + float(user_seconds), result.stdout


def python(dirpath: Path) -> Triple:
    """Run a Python solution."""
    return execute_command(["python", dirpath / "solution.py"])


def racket(dirpath: Path) -> Triple:
    """Run a Racket solution."""
    return execute_command(["racket", dirpath / "solution.rkt"])


def rust(dirpath: Path) -> Triple:
    """Run a Rust solution."""
    return execute_command(["cargo", "run", "--quiet", "--manifest-path", dirpath / "Cargo.toml"])


def fsharp(dirpath: Path) -> Triple:
    """Run an F# solution"""
    return execute_command(["dotnet", "fsi", dirpath / "solution.fsx"])


def ocaml(dirpath: Path) -> Triple:
    """Run an OCaml solution."""
    return execute_command(["ocaml", dirpath / "solution.ml"])


def jupyter(dirpath: Path) -> Triple:
    """Run a Jupyter notebook."""
    return execute_command(["ipython", "-c", f"%run {dirpath / 'solution.ipynb'}"])
