"""Run every solution."""

import subprocess
import time
from pathlib import Path
from typing import Final, Optional, Mapping, Type
from abc import ABC, abstractmethod


class Runtime(ABC):
    @classmethod
    @abstractmethod
    def run(cls, *args, **kwargs) -> None:
        """Run the code."""

    @classmethod
    @abstractmethod
    def can_run(cls, *args, **kwargs) -> bool:
        """Whether we can run the code"""


class PythonRuntime(Runtime):
    @classmethod
    def run(cls, dirpath: Path, *args: str) -> None:
        for filepath in dirpath.iterdir():
            if filepath.suffix == ".py":
                command = ["python", filepath]
                print("Running", command)
                subprocess.run(command)

    @classmethod
    def can_run(cls, dirpath: Path) -> bool:
        for filepath in dirpath.iterdir():
            if filepath.suffix == ".py":
                return True
        return False


# Languages and their commands
RUNTIMES: Final = {
    PythonRuntime,
}


def measure_execution_time(dirpath: Path, ext: Type[Runtime]) -> Optional[str]:
    # Use the licence as input while testing.
    start = time.time()
    try:
        ext.run(dirpath)
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
    results: dict[Path, str] = {}
    path = Path(".")
    for dirpath, _, filenames in path.walk():
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            for ext in RUNTIMES:
                if ext.can_run(dirpath):
                    if temp := measure_execution_time(dirpath, ext):
                        results[dirpath] = temp

    update_readme(results)


if __name__ == "__main__":
    main()
