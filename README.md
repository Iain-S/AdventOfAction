# AdventOfAction

Run AoC problems with a GitHub action.

## Development Setup

1. Install Python 3.13.
2. Install Pyre-check, with `pip install pyre-check`.
3. Install the pre-commit hooks with `pre-commit install --install-hooks`.
4. You're good to go.

## Running Tests

```bash
cd .github/actions/run-benchmarks
python test_run_benchmarks.py
```

## Using the Action

See [functional_tests.yaml](.github/workflows/functional_tests.yaml).

You may want to commit and push the changes to your branch with

```yaml
- name: Commit results
  shell: bash
  run: |
    git config --global user.name "github-actions[bot]"
    git config --global user.email "github-actions@github.com"
    git add README.md
    git commit -m "Update README with results" || echo "No changes to commit"
    git push
```

See [run_solutions.yaml](.github/workflows/run_solutions.yaml).
