import shutil
import unittest
from pathlib import Path, PosixPath
from unittest.mock import call, patch

from advent_of_action import main, runners


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        Path("./README.md").unlink(missing_ok=True)

    def test_main(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "helloo"
            mock_run.return_value.stderr = "1792,0.01,0.02"
            Path("README.md").write_text("")
            main.main()
            timings: list[str] = ["/usr/bin/time", "-f", "%M,%S,%U"]
            a: tuple[list[str], ...] = tuple(
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

    def test_measure_one(self) -> None:
        # Check that we measure the run.
        actual = main.measure_execution_time(("answer", "answer"), Path("."), lambda x, y: (1792, 0.03, "answer"))
        expected = ("0.03", "1792", ""), ("0.03", "1792", "")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_two(self) -> None:
        # Check that we .strip() the result.
        actual = main.measure_execution_time(("answer", "answer"), Path("."), lambda x, y: (1792, 0.03, "answer\n"))
        expected = ("0.03", "1792", ""), ("0.03", "1792", "")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_three(self) -> None:
        # Check that we check the answer.
        actual = main.measure_execution_time(
            ("answer", "answer"), Path("."), lambda x, y: (1792, 0.03, "wrong answer\n")
        )
        expected = ("", "", "Different answer"), ("", "", "Different answer")
        self.assertEqual(
            expected,
            actual,
        )

    def test_measure_four(self) -> None:
        # Check that we check the answer.
        def bad_runner(_: Path, __: str) -> tuple[int, float, str]:
            return runners.execute_command(["bash", "-c", "exit 1"])

        actual = main.measure_execution_time(("", ""), Path("."), bad_runner)
        expected = ("", "", "Error (1)"), ("", "", "Error (1)")
        self.assertTupleEqual(
            expected,
            actual,
        )

    def test_measure_five(self) -> None:
        # Check that we check the answer.
        def partial_runner(_: Path, part: str) -> tuple[int, float, str]:
            if part == "one":
                return 1792, 0.03, "answer"
            return 1792, 0.03, "wrong answer"

        actual = main.measure_execution_time(("answer", "answer"), Path("."), partial_runner)
        expected = (("0.03", "1792", ""), ("", "", "Different answer"))
        self.assertTupleEqual(
            expected,
            actual,
        )

    def test_execute_command(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "hello"
            mock_run.return_value.stderr = "1792,0.01,0.02"
            actual = runners.execute_command(
                [],
            )
        self.assertEqual(actual[0], 1792)
        self.assertEqual(actual[1], 0.01 + 0.02)
        self.assertEqual(
            "hello",
            actual[2],
        )

    def test_write_results(self) -> None:
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
        readme = Path("README.md")
        shutil.copy(Path("README_TEMPLATE_2.md"), readme)
        expected_readme_txt = Path("EXPECTED_README_3.md").read_text()

        run = ("01", "python", "iain")
        stat = ("0.01", "1792", "")

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())

        main.write_results({run: (stat, stat)})
        self.assertEqual(expected_readme_txt, readme.read_text())


if __name__ == "__main__":
    unittest.main()
