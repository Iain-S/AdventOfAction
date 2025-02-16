"""Runners for various programming languages."""

import os
import subprocess
from abc import ABC
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path

type kilobytes = int
type seconds = float
type output = str
type Triple = tuple[kilobytes, seconds, output]
type RunnerFunc = Callable[[Path], Triple]


# make an enum for part one or two
class Part(StrEnum):
    ONE = "one"
    TWO = "two"


class Runner(ABC):
    """A runner for a programming language."""

    @classmethod
    def setup(cls, dirpath: Path) -> Triple:
        raise NotImplementedError

    @classmethod
    def run(cls, dirpath: Path, part: Part) -> Triple:
        raise NotImplementedError

    @classmethod
    def teardown(cls, dirpath: Path) -> Triple:
        raise NotImplementedError


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


class PythonRunner(Runner):
    """Run a Python solution."""

    @classmethod
    def setup(cls, dirpath: Path) -> Triple:
        return execute_command(["pip", "install", "-r", str(dirpath / "requirements.txt")])

    @classmethod
    def run(cls, dirpath: Path, part: Part) -> Triple:
        return execute_command(["python", str(dirpath / "solution.py"), part.value])

    @classmethod
    def teardown(cls, dirpath: Path) -> Triple:
        return execute_command(["pip", "uninstall", "-r", str(dirpath / "requirements.txt")])


# def racket(dirpath: Path, part: str) -> Triple:
#     """Run a Racket solution."""
#     return execute_command(["racket", str(dirpath / "solution.rkt"), part])


class RustRunner(Runner):
    """Run a Rust solution."""

    @classmethod
    def setup(cls, dirpath: Path) -> Triple:
        return execute_command(["cargo", "build", "--manifest-path", str(dirpath / "Cargo.toml")])

    @classmethod
    def run(cls, dirpath: Path, part: Part) -> Triple:
        return execute_command(["cargo", "run", "--quiet", "--manifest-path", str(dirpath / "Cargo.toml"), part.value])

    @classmethod
    def teardown(cls, dirpath: Path) -> Triple:
        return 0, 0, "Nothing to do"


# def fsharp(dirpath: Path, part: str) -> Triple:
#     """Run an F# solution."""
#     return execute_command(["dotnet", "fsi", str(dirpath / "solution.fsx"), part])


# def ocaml(dirpath: Path, part: str) -> Triple:
#     """Run an OCaml solution."""
#     return execute_command(["ocaml", str(dirpath / "solution.ml"), part])


# def jupyter(dirpath: Path, part: str) -> Triple:
#     """Run a Jupyter notebook."""
#     return execute_command(["ipython", "-c", f"%run {dirpath / 'solution.ipynb'}", part])
