"""Runners for various programming languages."""

import subprocess
from collections.abc import Callable
from pathlib import Path

type Triple = tuple[int, float, str]
type RunnerFunc = Callable[[Path, str], Triple]


def execute_command(command: list[str | Path]) -> Triple:
    """Execute a command and return the memory usage, time and stdout."""
    print("Running", command)
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%M,%S,%U"] + command, capture_output=True, timeout=60, text=True, check=True
    )
    kilobytes, sys_seconds, user_seconds = result.stderr.split(",")
    return int(kilobytes), float(sys_seconds) + float(user_seconds), result.stdout


def python(dirpath: Path, part: str) -> Triple:
    """Run a Python solution."""
    return execute_command(["python", str(dirpath / "solution.py"), part])


def racket(dirpath: Path, part: str) -> Triple:
    """Run a Racket solution."""
    return execute_command(["racket", str(dirpath / "solution.rkt"), part])


def rust(dirpath: Path, part: str) -> Triple:
    """Run a Rust solution."""
    return execute_command(["cargo", "run", "--quiet", "--manifest-path", str(dirpath / "Cargo.toml"), part])


def fsharp(dirpath: Path, part: str) -> Triple:
    """Run an F# solution."""
    return execute_command(["dotnet", "fsi", str(dirpath / "solution.fsx"), part])


def ocaml(dirpath: Path, part: str) -> Triple:
    """Run an OCaml solution."""
    return execute_command(["ocaml", str(dirpath / "solution.ml"), part])


def jupyter(dirpath: Path, part: str) -> Triple:
    """Run a Jupyter notebook."""
    return execute_command(["ipython", "-c", f"%run {dirpath / 'solution.ipynb'}", part])
