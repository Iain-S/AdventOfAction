import importlib
import subprocess
import unittest
from pathlib import PosixPath, Path
from unittest.mock import patch, call
from advent_of_action import main  # type: ignore


class TestMain(unittest.TestCase):
    def test_main(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "hello\n1792,0.01,0.02"
            # Need to explicitly (re)load the module
            # so that the call to partial() works on the
            # patched subprocess.run.
            aoa = importlib.import_module("advent_of_action.main")
            aoa = importlib.reload(aoa)
            aoa.main()
            timings = ["/usr/bin/time", "-f", "%M,%S,%U"]
            self.assertListEqual(
                mock_run.call_args_list,
                [
                    call(
                        timings + x,  # type: ignore
                        capture_output=True,
                        timeout=60,
                        text=True,
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
                            "racket",
                            PosixPath("day_99/racket_iain/solution.rkt"),
                        ],
                        [
                            "cargo",
                            "run",
                            "--manifest-path",
                            PosixPath("day_99/rust_iain/Cargo.toml"),
                        ],
                    )
                ],
            )

    def test_measure_one(self) -> None:
        # Check that we measure the run.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "answer"))
        expected = "0 sec"
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_two(self) -> None:
        # Check that we .strip() the result.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "answer\n"))
        expected = "0 sec"
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_three(self) -> None:
        # Check that we check the answer.
        actual = main.measure_execution_time(Path("."), lambda x: (1792, 0.03, "wrong answer\n"))
        expected = "Wrong answer"
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_four(self) -> None:
        # Check that we check the answer.
        def raises(
            _,
        ) -> str:
            raise subprocess.CalledProcessError(
                1,
                "cmd",
            )

        actual = main.measure_execution_time(
            Path("."),
            raises,
        )
        expected = "Error (1)"
        self.assertEqual(
            expected,
            actual,
        )

    def test_execute_command(self) -> None:
        with patch("advent_of_action.main.SUBPROCESS_RUN") as mock_run:
            mock_run.return_value.stdout = "hello\n1792,0.01,0.02"
            actual = main.execute_command(
                [],
            )
        self.assertEqual(actual[0], 1792)
        self.assertEqual(actual[1], 0.01 + 0.02)
        self.assertEqual(
            "hello",
            actual[2],
        )


if __name__ == "__main__":
    unittest.main()
