import unittest
from pathlib import Path, PosixPath
from unittest.mock import call, patch

from advent_of_action import main  # type: ignore


class TestMain(unittest.TestCase):
    def test_main(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "helloo"
            mock_run.return_value.stderr = "1792,0.01,0.02"
            # Need to explicitly (re)load the module
            # so that the call to partial() works on the
            # patched subprocess.run.
            main.main()
            timings = ["/usr/bin/time", "-f", "%M,%S,%U"]
            self.assertListEqual(
                mock_run.call_args_list,
                [
                    call(
                        timings + x,  # type: ignore
                        capture_output=True,
                        timeout=60,
                        text=True,
                        check=True,
                    )
                    for x in (
                        [
                            "dotnet",
                            "fsi",
                            PosixPath("day_99/fsharp_iain/solution.fsx"),
                        ],
                        [
                            "ipython",
                            "-c",
                            f"%run {PosixPath('day_99/jupyter_iain/solution.ipynb')}",
                        ],
                        [
                            "ocaml",
                            PosixPath("day_99/ocaml_iain/solution.ml"),
                        ],
                        [
                            "python",
                            PosixPath("day_99/python_iain/solution.py"),
                        ],
                        [
                            "python",
                            PosixPath("day_99/python_nain/solution.py"),
                        ],
                        [
                            "python",
                            PosixPath("day_99/python_zain/solution.py"),
                        ],
                        [
                            "racket",
                            PosixPath("day_99/racket_iain/solution.rkt"),
                        ],
                        [
                            "cargo",
                            "run",
                            "--quiet",
                            "--manifest-path",
                            PosixPath("day_99/rust_iain/Cargo.toml"),
                        ],
                    )
                ],
            )

    def test_measure_one(self) -> None:
        # Check that we measure the run.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "answer"))
        expected = ("0.03 sec", "1792 KB", "")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_two(self) -> None:
        # Check that we .strip() the result.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "answer\n"))
        expected = ("0.03 sec", "1792 KB", "")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_three(self) -> None:
        # Check that we check the answer.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "wrong answer\n"))
        expected = "", "", "Different answer"
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_four(self) -> None:
        # Check that we check the answer.
        def bad_runner(_: Path) -> tuple[int, float, str]:
            return main.execute_command(["bash", "-c", "exit 1"])

        actual = main.measure_execution_time(Path("."), bad_runner)
        expected = "", "", "Error (1)"
        self.assertEqual(
            expected,
            actual,
        )

    def test_execute_command(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "hello"
            mock_run.return_value.stderr = "1792,0.01,0.02"
            actual = main.execute_command(
                [],
            )
        self.assertEqual(actual[0], 1792)
        self.assertEqual(actual[1], 0.01 + 0.02)
        self.assertEqual(
            "hello",
            actual[2],
        )

    def test_write_results(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
