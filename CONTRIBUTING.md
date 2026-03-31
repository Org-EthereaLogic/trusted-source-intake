# Contributing

Thank you for your interest in this project. This repository is part of the
**Enterprise Data Trust** portfolio by Anthony Johnson / EthereaLogic LLC.

## Scope

This project demonstrates a source intake control pattern for Databricks.
Contributions should stay within that scope: improving the SQL pipeline,
strengthening the contract checks, expanding test coverage, or improving
documentation.

## Development Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Pull Request Guidelines

1. All tests must pass.
2. New features must include tests.
3. Ruff must report zero issues.
4. Commit messages should follow conventional commit format.
