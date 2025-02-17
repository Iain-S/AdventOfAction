"""Runners for various programming languages."""

import os
import subprocess
from collections.abc import Callable, Generator
from pathlib import Path

type KB = int
type seconds = float
type output = str
type Triple = tuple[KB, seconds, output]
type RunnerFunc = Callable[[Path], Generator[Triple]]


def execute_command(command: list[str | Path], timeout: float = float(os.environ["TIMEOUT_SECONDS"])) -> Triple:
    """Execute a command and return the memory usage, time and stdout."""
    print("Running", command)
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%M,%S,%U"] + command,
        capture_output=True,
        timeout=timeout,
        text=True,
        check=True,
    )
    kilobytes, sys_seconds, user_seconds = result.stderr.split(",")
    return int(kilobytes), float(sys_seconds) + float(user_seconds), result.stdout.strip()


def python_runner(dirpath: Path) -> Generator[Triple]:
    """Run a Python solution."""
    yield execute_command(["pip", "install", "-r", str(dirpath / "requirements.txt")])
    yield execute_command(["python", str(dirpath / "solution.py"), "one"])
    yield execute_command(["python", str(dirpath / "solution.py"), "two"])
    yield execute_command(["pip", "uninstall", "-r", str(dirpath / "requirements.txt")])


# def racket(dirpath: Path, part: str) -> Triple:
#     """Run a Racket solution."""
#     return execute_command(["racket", str(dirpath / "solution.rkt"), part])


def rust_runner(dirpath: Path) -> Generator[Triple]:
    """Run a Rust solution."""
    yield execute_command(["cargo", "build", "--manifest-path", str(dirpath / "Cargo.toml")])
    yield execute_command(["cargo", "run", "--quiet", "--manifest-path", str(dirpath / "Cargo.toml"), "one"])
    yield execute_command(["cargo", "run", "--quiet", "--manifest-path", str(dirpath / "Cargo.toml"), "two"])
    yield 0, 0, "Nothing to do"


# def fsharp(dirpath: Path, part: str) -> Triple:
#     """Run an F# solution."""
#     return execute_command(["dotnet", "fsi", str(dirpath / "solution.fsx"), part])


# def ocaml(dirpath: Path, part: str) -> Triple:
#     """Run an OCaml solution."""
#     return execute_command(["ocaml", str(dirpath / "solution.ml"), part])


# def jupyter(dirpath: Path, part: str) -> Triple:
#     """Run a Jupyter notebook."""
#     return execute_command(["ipython", "-c", f"%run {dirpath / 'solution.ipynb'}", part])
