# Executive Mode

Chapter One is the portfolio entry point. Install this repository first.

It contains:

- `Open Executive Demo.command`
- `scripts/executive_mode.py`
- this guide

The launcher expects Chapters 2 and 3 to live as sibling folders beside
`trusted-source-intake` in the same parent directory. If they are missing, the
launcher clones them automatically.

## What Executive Mode Does

`Open Executive Demo.command` launches `scripts/executive_mode.py`, which:

1. Confirms the machine can run the portfolio.
2. Clones any missing chapter repositories into the same parent directory as
   Chapter One.
3. Selects a supported Python runtime (3.10+).
4. Creates repo-local virtual environments and installs each chapter in
   editable mode.
5. Runs one guided demo per chapter.
6. Writes an executive summary report to `docs/executive_mode_report.md` and
   `docs/executive_mode_report.html` inside Chapter One.

## Fastest Path

### macOS

1. Clone `trusted-source-intake`.
2. Open the Chapter One folder.
3. Double-click `Open Executive Demo.command`.
4. Wait for the launcher to finish.
5. Read the generated report in your browser.

If you prefer the terminal:

```bash
python3 scripts/executive_mode.py all --open-report
```

## What the Report Shows

For each chapter, the report records three verdicts:

- `Acquire/Open`: the repo is present, readable, and includes its proof files.
- `Guided Demo`: the local demo ran successfully from the repo-local
  environment.
- `Databricks Surface`: whether Databricks-specific validation is available on
  this machine. Local demo success is reported separately from live Databricks
  access.

## Expected Demo Outcomes

- Chapter 1: the intake demo prints the handoff summary with 33 landed rows,
  10 ready rows, and 23 quarantined rows.
- Chapter 2: the release-control demo intentionally ends in `Overall Verdict:
  FAIL` because the drifted sample is designed to block Gold publication.
- Chapter 3: the benchmark demo ends in `Overall Verdict: PASS` and writes a
  JSON evidence bundle under `runs/`.

## Troubleshooting

### No supported Python found

The launcher looks for Python 3.10 or newer. If none is available and Homebrew
is installed, it attempts to install `python@3.12`.

### Databricks validation is blocked

That is expected unless the machine already has both:

- a `databricks` CLI binary on `PATH`
- a `~/.databrickscfg` file with approved credentials

Executive Mode does not create or copy Databricks credentials.

### I want the deeper technical walkthrough

Use the chapter READMEs after Executive Mode finishes:

- `README.md` in Chapter One
- `../silent-failure-prevention/README.md` in Chapter Two
- `../measurable-control-effectiveness/README.md` in Chapter Three

