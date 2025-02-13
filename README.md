# AdventOfAction

Run AoC problems with a GitHub action.

## Development Setup

1. Install Poetry.
2. Install Advent of Action, with `poetry install`.
3. Install the pre-commit hooks with `pre-commit install --install-hooks`.
4. You're good to go.

## Running Tests

```bash
cd tests
python test_main.py
```

## Using the Action

See [functional_tests.yaml](.github/workflows/functional_tests.yaml).

You may want to commit and push the changes to your branch with:

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

If you'd like to opt out of having your code executed, add an `.optout` file to your directory for that day.

For each day, provide an input file named `input.gpg` and a solution file named `answers.gpg`. Provide the encryption/decryption passphrase as the `gpg-passphrase` input.
