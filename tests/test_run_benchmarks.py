import importlib
import subprocess
import unittest
from pathlib import PosixPath, Path
from unittest.mock import patch, call
from advent_of_action import run_benchmarks


class TestRunBenchmarks(unittest.TestCase):
    def test_main(self) -> None:
        with patch("subprocess.run") as mock_run:
            # Need to explicitly (re)load the module
            # so that the call to partial() works on the
            # patched subprocess.run.
            benchmarks = importlib.import_module("advent_of_action.run_benchmarks")
            benchmarks = importlib.reload(benchmarks)
            benchmarks.main()
            mock_run.assert_has_calls(
                [
                    call(
                        ["python", PosixPath("day_99/python_iain/solution.py")],
                        capture_output=True,
                        timeout=60,
                    ),
                    call(
                        ["racket", PosixPath("day_99/racket_iain/solution.rkt")],
                        capture_output=True,
                        timeout=60,
                    ),
                ],
                any_order=True,
            )

    def test_measure_one(self) -> None:
        # Check that we measure the run.
        actual = run_benchmarks.measure_execution_time(Path("."), lambda x: "answer")
        expected = "0.000 sec"
        self.assertEqual(expected, actual)

    def test_measure_two(self) -> None:
        # Check that we .strip() the result.
        actual = run_benchmarks.measure_execution_time(Path("."), lambda x: "answer\n")
        expected = "0.000 sec"
        self.assertEqual(expected, actual)

    def test_measure_three(self) -> None:
        # Check that we check the answer.
        actual = run_benchmarks.measure_execution_time(
            Path("."), lambda x: "wrong answer"
        )
        expected = "Wrong answer"
        self.assertEqual(expected, actual)

    def test_measure_four(self) -> None:
        # Check that we check the answer.
        def raises(_) -> str:
            raise subprocess.CalledProcessError(1, "cmd")

        actual = run_benchmarks.measure_execution_time(
            Path("."),
            raises,
        )
        expected = "Error (1)"
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
