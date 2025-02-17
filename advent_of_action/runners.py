"""Runners for various programming languages."""

import os
import subprocess
from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

type kilobytes = int
type seconds = float
type output = str
type Triple = tuple[kilobytes, seconds, output]
type RunnerFunc = Callable[[Path], Triple]


# make an enum for part one or two
class Part(StrEnum):
    SETUP= "setup"
    ONE = "one"
    TWO = "two"
    TEARDOWN = "teardown"


@dataclass
class Command(ABC):
    """A runner for a programming language."""

    setup: list[str]
    run: list[str]
    teardown: list[str]


PYTHON: Final = Command(
    setup=["pip", "install", "-r", "requirements.txt"],
    run=["python", "solution.py"],
    teardown=["pip", "uninstall", "-r", "requirements.txt"],
)

RUST: Final = Command(
    setup=["cargo", "build"],
    run=["cargo", "run"],
    teardown=["sleep", "0"],
)

RACKET: Final = Command(
    setup=["sleep", "0"],
    run=["racket", "solution.rkt"],
    teardown=["sleep", "0"],
)

OCAML: Final = Command(
    setup=["sleep", "0"],
    run=["ocaml", "solution.ml"],
    teardown=["sleep", "0"],
)
FSHARP: Final = Command(
    setup=["sleep", "0"],
    run=["dotnet", "fsi", "solution.fsx"],
    teardown=["sleep", "0"],
)
JUPYTER: Final = Command(
    setup=["cargo", "build"],
    run=["ipython", "-c", "%run 'solution.ipynb'"],
    teardown=["sleep", "0"]
)
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