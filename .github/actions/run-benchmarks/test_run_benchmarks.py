import unittest
from pathlib import PosixPath
from types import TracebackType
from unittest.mock import patch, call
import os
import run_benchmarks  # type: ignore


class Chdir:
    def __init__(self, new: str) -> None:
        self.new = new
        self.cwd: str = os.getcwd()

    def __enter__(self) -> None:
        os.chdir(self.new)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        os.chdir(self.cwd)


class TestRunBenchmarks(unittest.TestCase):
    def test_main(self) -> None:
        with Chdir("../../.."):
            with patch("subprocess.run") as mock_run:
                run_benchmarks.main()
                self.assertListEqual(
                    mock_run.call_args_list,
                    [
                        call(
                            ["python", PosixPath("day_99/python_iain/solution.py")],
                            capture_output=True,
                        ),
                        call(
                            ["racket", PosixPath("day_99/racket_iain/solution.rkt")],
                            capture_output=True,
                        ),
                    ],
                )


if __name__ == "__main__":
    unittest.main()
