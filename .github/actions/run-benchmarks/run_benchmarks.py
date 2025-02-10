"""Run every solution."""

import os
import subprocess
import time
from pathlib import Path
from typing import Final, Optional, Mapping

# Languages and their commands
RUNTIMES: Final = {".py": "python3", ".js": "node", ".sh": "bash"}


def measure_execution_time(filepath: Path) -> Optional[str]:
    ext = os.path.splitext(filepath)[1]
    if ext not in RUNTIMES:
        return "None"  # Skip unsupported files

    # Use the licence as input while testing.
    command = [RUNTIMES[ext], filepath, "./LICENSE"]
    start = time.time()
    try:
        print("Running", command)
        subprocess.run(command, capture_output=True, text=True, check=True)
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


if __name__ == "__main__":
    results: dict[Path, str] = {}
    path = Path(".")
    for dirpath, _, filenames in path.walk():
        if dirpath.parts and dirpath.parts[0].startswith("day_"):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in RUNTIMES):
                    if temp := measure_execution_time(dirpath / filename):
                        results[dirpath / filename] = temp

    update_readme(results)
