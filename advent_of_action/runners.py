"""Runners for various programming languages."""

import os
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

type kilobytes = int
type seconds = float
type output = str
type Triple = tuple[kilobytes, seconds, output]
type command = list[str | Path]


class Part(StrEnum):
    """The parts of a day's solution."""

    SETUP = "setup"
    ONE = "one"
    TWO = "two"
    TEARDOWN = "teardown"


@dataclass
class Commands:
    """A runner for a programming language."""

    setup: command
    run: command
    teardown: command


PYTHON: Final = Commands(
    setup=["pip", "install", "-q", "-q", "-q", "--no-input", "-r", "requirements.txt"],
    run=["python", "solution.py"],
    teardown=["pip", "uninstall", "-q", "-q", "-q", "--no-input", "-r", "requirements.txt"],
)

RUST: Final = Commands(
    setup=["cargo", "build", "--quiet"],
    run=["cargo", "run", "--quiet"],
    teardown=[],
)

RACKET: Final = Commands(
    setup=[],
    run=["racket", "solution.rkt"],
    teardown=[],
)

OCAML: Final = Commands(
    setup=[],
    run=["ocaml", "solution.ml"],
    teardown=[],
)
FSHARP: Final = Commands(
    setup=[],
    run=["dotnet", "fsi", "solution.fsx"],
    teardown=[],
)
JUPYTER: Final = Commands(setup=[], run=["ipython", "-c", "%run 'solution.ipynb'"], teardown=[])


def execute_command(cmd: command, timeout: float | None = None) -> Triple:
    """Execute a command and return the memory usage, time and stdout."""
    if timeout is None:
        timeout = float(os.environ["TIMEOUT_SECONDS"])
    print("Running", cmd)
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%M,%S,%U"] + cmd,
        capture_output=True,
        timeout=timeout,
        text=True,
        check=True,
    )
    kilobytes, sys_seconds, user_seconds = result.stderr.split(",")
    return int(kilobytes), float(sys_seconds) + float(user_seconds), result.stdout.strip()
