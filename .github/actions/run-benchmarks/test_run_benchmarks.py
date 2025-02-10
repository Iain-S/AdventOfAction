import unittest
from pathlib import PosixPath
from types import TracebackType
from unittest.mock import patch
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
            with patch("run_benchmarks.measure_execution_time") as mock_measure:
                run_benchmarks.main()
                mock_measure.assert_called_once_with(
                    PosixPath("day_99/racket_iain"), run_benchmarks.run_racket
                )


if __name__ == "__main__":
    unittest.main()
