"""Run every solution."""

import os
import subprocess
import time

# Languages and their commands
RUNTIMES = {".py": "python3", ".js": "node", ".sh": "bash"}


def measure_execution_time(filepath):
    ext = os.path.splitext(filepath)[1]
    if ext not in RUNTIMES:
        return None  # Skip unsupported files

    # Use the licence as input while testing.
    command = [RUNTIMES[ext], filepath, "./LICENSE"]
    start = time.time()
    try:
        print("Running", command)
        subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return f"Error ({e.returncode})"
    return f"{time.time() - start:.3f} sec"


def update_readme(the_results):
    readme_path = "README.md"
    new_content = "\n## Benchmark Results\n"
    for the_path, time_taken in the_results.items():
        new_content += f"- `{the_path}`: {time_taken}\n"

    with open(readme_path, "a") as f:
        f.write(new_content)


if __name__ == "__main__":
    results = {}
    for root, _, files in os.walk("."):
        if root.startswith("./day"):
            for file in files:
                if any(file.endswith(ext) for ext in RUNTIMES):
                    path = os.path.join(root, file)
                    results[path] = measure_execution_time(path)

    update_readme(results)
