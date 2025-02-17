"""Tests for the main module."""

import os
import shutil
import subprocess
import unittest
from pathlib import Path, PosixPath
from subprocess import run
from unittest.mock import MagicMock, call, patch

from advent_of_action import main, runners


class TestMain(unittest.TestCase):
    """Most of the tests for main.py."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test environment for the class."""
        os.environ["GPG_PASS"] = "yourpassword"
        os.environ["TIMEOUT_SECONDS"] = "60"

        # For example, if we're on macOS.
        def new_run(command, *args, **kwargs):  # type: ignore
            command = ["gtime"] + command[1:]
            return run(command, *args, **kwargs)

        if shutil.which("gtime"):
            patch("subprocess.run", new=new_run).start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down the test environment for the class."""
        patch.stopall()

    def setUp(self) -> None:
        """Set up the test environment for each function."""
        # Undo anything that might have been set by failing tests.
        Path("./README.md").unlink(missing_ok=True)
        Path("./input.txt").unlink(missing_ok=True)

    @patch("subprocess.run", autospec=True)
    def test_main(self, mock_run: MagicMock) -> None:
        """We should run all the solutions."""
        mock_run.return_value.stdout = "helloo"
        mock_run.return_value.stderr = "1792,0.01,0.02"
        Path("README.md").write_text("")
        main.main()
        timings = ["/usr/bin/time", "-f", "%M,%S,%U"]
        a = (
            [["dotnet", "fsi", str(PosixPath("day_99/fsharp_iain/solution.fsx")), x] for x in ("one", "two")]
            + [
                ["ipython", "-c", f"%run {str(PosixPath('day_99/jupyter_iain/solution.ipynb'))}", x]
                for x in ("one", "two")
            ]
            + [["ocaml", str(PosixPath("day_99/ocaml_iain/solution.ml")), x] for x in ("one", "two")]
            + [["python", str(PosixPath("day_99/python_iain/solution.py")), x] for x in ("one", "two")]
            + [
                [
                    "python",
                    str(PosixPath("day_99/python_zain/solution.py")),
                    x,
                ]
                for x in ("one", "two")
            ]
            + [["racket", str(PosixPath("day_99/racket_iain/solution.rkt")), x] for x in ("one", "two")]
            + [
                ["cargo", "run", "--quiet", "--manifest-path", str(PosixPath("day_99/rust_iain/Cargo.toml")), x]
                for x in ("one", "two")
            ]
        )
        self.assertListEqual(
            mock_run.call_args_list,
            [
                call(
                    timings + x,
                    capture_output=True,
                    timeout=60,
                    text=True,
                    check=True,
                )
                for x in a
            ],
        )

    @patch("subprocess.run", autospec=True)
    def test_main_two(self, mock_run: MagicMock) -> None:
        """We shouldn't re-run a solution that we have stats for."""
        mock_run.return_value.stdout = "helloo"
        mock_run.return_value.stderr = "1792,0.01,0.02"
        shutil.copy(Path("README_TEMPLATE_3.md"), Path("README.md"))
        main.main()
        timings = ["/usr/bin/time", "-f", "%M,%S,%U"]
        a = [["dotnet", "fsi", str(PosixPath("day_99/fsharp_iain/solution.fsx")), x] for x in ("one", "two")] + [
            ["cargo", "run", "--quiet", "--manifest-path", str(PosixPath("day_99/rust_iain/Cargo.toml")), x]
            for x in ("one", "two")
        ]
        self.assertListEqual(
            mock_run.call_args_list,
            [
                call(
                    timings + x,
                    capture_output=True,
                    timeout=60,
                    text=True,
                    check=True,
                )
                for x in a
            ],
        )

    def test_measure_one(self) -> None:
        """Check that we can measure the execution time of a solution."""

        def mock_runner(_: Path) -> runners.TripleGenerator:
            yield 1, 0.0, "setup"
            yield 1792, 0.03, "answer"
            yield 1792, 0.03, "answer"
            yield 1, 0.3, "teardown"

        actual = main.measure_execution_time(("answer", "answer"), Path("."), mock_runner)
        expected = ("0.03", "1792", ""), ("0.03", "1792", "")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_two(self) -> None:
        """Check that we can handle a wrong answer."""

        def wrong_answer_generator(_: Path) -> runners.TripleGenerator:
            yield (1792, 0.03, "setup")
            yield (1792, 0.03, "wrong answer\n")
            yield (1792, 0.03, "wrong answer\n")
            yield (1792, 0.03, "teardown")

        actual = main.measure_execution_time(("answer", "answer"), Path("."), wrong_answer_generator)
        expected = ("", "", "Different answer"), ("", "", "Different answer")
        self.assertEqual(
            expected,
            actual,
        )

    @patch("builtins.print", autospec=True)
    def test_measure_three(self, mock_print: MagicMock) -> None:
        """Check that we can handle a non-zero exit code."""

        def bad_runner(_: Path) -> runners.TripleGenerator:
            yield 1, 0.1, "setup"
            yield runners.execute_command(["bash", "-c", "exit 1"])
            yield runners.execute_command(["bash", "-c", "exit 1"])
            yield 1, 0.1, "teardown"

        actual = main.measure_execution_time(("", ""), Path("."), bad_runner)
        expected = ("", "", "Error (1)"), ("", "", "Error (1)")
        self.assertTupleEqual(
            expected,
            actual,
        )

        mock_print.assert_called_with("Command exited with non-zero status 1")

    @patch("builtins.print", autospec=True)
    def test_measure_four(self, mock_print: MagicMock) -> None:
        """Check that we can handle a partially wrong answer."""
        # Check that we check the answer.

        def partial_runner(_: Path) -> runners.TripleGenerator:
            yield 1, 0.01, "setup"
            yield 1792, 0.03, "answer"
            yield 1792, 0.03, "wrong answer"
            yield 1, 0.01, "teardown"

        actual = main.measure_execution_time(("answer", "answer"), Path("."), partial_runner)
        expected = (("0.03", "1792", ""), ("", "", "Different answer"))
        self.assertTupleEqual(
            expected,
            actual,
        )
        mock_print.assert_called_with("Incorrect answer for part two: wrong answer")

    @patch("builtins.print", autospec=True)
    def test_measure_five(self, mock_print: MagicMock) -> None:
        """Check that we can handle a timeout."""

        def raise_timeout(*args, **kwargs):  # type: ignore
            raise subprocess.TimeoutExpired("cmd", 6)

        actual = main.measure_execution_time(("", ""), Path("."), raise_timeout)
        expected = ("", "", "Timeout"), ("", "", "Timeout")
        self.assertTupleEqual(
            expected,
            actual,
        )
        mock_print.assert_called_with("Command timed out after 6 seconds")

    @patch("subprocess.run", autospec=True)
    def test_execute_command(self, mock_run: MagicMock) -> None:
        """Executing a command should return the memory usage, time and stdout."""
        mock_run.return_value.stdout = "hello\n"
        mock_run.return_value.stderr = "1792,0.01,0.02"
        actual = runners.execute_command(
            [],
        )
        self.assertTupleEqual(
            actual,
            (
                1792,
                0.01 + 0.02,
                "hello",
            ),
        )

    def test_write_results(self) -> None:
        """Check we can write to a README with some existing stats."""
        readme = Path("README.md")
        shutil.copy(Path("README_TEMPLATE.md"), readme)
        expected_readme_txt = Path("EXPECTED_README_2.md").read_text()

        run = ("01", "python", "iain")
        stat = ("0.01", "1792", "")

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())

    def test_write_results_two(self) -> None:
        """Check we can write to a README with no existing stats."""
        readme = Path("README.md")
        shutil.copy(Path("README_TEMPLATE_2.md"), readme)
        expected_readme_txt = Path("EXPECTED_README_3.md").read_text()

        run = ("01", "python", "iain")
        stat = ("0.01", "1792", "")

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())

    def test_get_answers(self) -> None:
        """Test that we can get the answers from an encrypted file."""
        actual = main.get_answers(Path("day_99/"))
        self.assertEqual(("answer", "answer2"), actual)

    def test_from_table(self) -> None:
        """Test that we can convert a table to a dictionary."""
        actual = main.from_table(
            "\n"
            + "\n"
            + "## Stats\n"
            + "\n"
            + "| day | language | who | part | time (s) | mem (KB) | notes |\n"
            + "| --- | --- | --- | --- | --- | --- | --- |\n"
            + "| 01 | python | iain | one | 0.01 | 1792 | |\n"
            + "| 01 | python | iain | two | 0.01 | 1792 | |\n"
            + "\n"
            + "\n"
        )
        expected = {("01", "python", "iain"): (("0.01", "1792", ""), ("0.01", "1792", ""))}
        self.assertDictEqual(expected, actual)

    def test_from_table_raises(self) -> None:
        """We expect an error if the part isn't 'one' or 'two'."""
        with self.assertRaises(ValueError):
            main.from_table(
                "\n"
                + "\n"
                + "## Stats\n"
                + "\n"
                + "| day | language | who | part | time (s) | mem (KB) | notes |\n"
                + "| --- | --- | --- | --- | --- | --- | --- |\n"
                + "| 01 | python | iain | three | 0.01 | 1792 | |\n"
                + "\n"
                + "\n"
            )


class TestExpectsGPG(unittest.TestCase):
    """Test the functions that expect GPG_PASS to be set."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test environment for the class."""
        os.unsetenv("GPG_PASS")

    def test_get_answers_raises(self) -> None:
        """Test that get_answers raises an exception if GPG_PASS is missing."""
        with self.assertRaises(ValueError):
            main.get_answers(Path("day_99/"))

    def test_make_input_raises(self) -> None:
        """Test that make_input_file raises an exception if GPG_PASS is missing."""
        with self.assertRaises(ValueError):
            main.make_input_file(Path("day_99/"))


if __name__ == "__main__":
    unittest.main()
