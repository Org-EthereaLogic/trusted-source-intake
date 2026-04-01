#!/usr/bin/env python3
"""Executive launcher for the Enterprise Data Trust portfolio."""

from __future__ import annotations

import argparse
import html
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

CHAPTER_ONE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = CHAPTER_ONE_ROOT.parent
REPORT_MD = CHAPTER_ONE_ROOT / "docs" / "executive_mode_report.md"
REPORT_HTML = CHAPTER_ONE_ROOT / "docs" / "executive_mode_report.html"


@dataclass(frozen=True)
class Chapter:
    slug: str
    title: str
    repo_url: str
    demo_command: tuple[str, ...]
    demo_markers: tuple[str, ...]
    evidence_command: Optional[tuple[str, ...]] = None
    evidence_paths: tuple[str, ...] = ()
    proof_paths: tuple[str, ...] = ()
    databricks_bundle: bool = False
    expected_outcome: str = ""

    @property
    def path(self) -> Path:
        if self.slug == "trusted-source-intake":
            return CHAPTER_ONE_ROOT
        return WORKSPACE_ROOT / self.slug

    @property
    def readme(self) -> Path:
        return self.path / "README.md"

    @property
    def venv_bin(self) -> Path:
        return self.path / ".venv" / "bin"


@dataclass
class SurfaceResult:
    status: str
    summary: str
    command: str = ""
    stdout: str = ""
    stderr: str = ""


@dataclass
class ChapterResult:
    chapter: Chapter
    acquire_open: SurfaceResult
    guided_demo: SurfaceResult
    databricks_surface: SurfaceResult


CHAPTERS = (
    Chapter(
        slug="trusted-source-intake",
        title="Chapter 1: Trusted Source Intake",
        repo_url="https://github.com/Org-EthereaLogic/trusted-source-intake.git",
        demo_command=("intake-demo",),
        demo_markers=("Total landed:      33", "Replay duplicates: 10"),
        proof_paths=(
            "README.md",
            "notebooks/00_seed_demo_files.py",
            "notebooks/01_review_outputs.py",
            "databricks.yml",
            "resources/intake_pipeline.yml",
            "resources/refresh_demo.yml",
            "docs/executive_mode.md",
            "scripts/executive_mode.py",
        ),
        databricks_bundle=True,
        expected_outcome="Prints the offline handoff summary for the deterministic intake corpus.",
    ),
    Chapter(
        slug="silent-failure-prevention",
        title="Chapter 2: Silent Failure Prevention",
        repo_url="https://github.com/Org-EthereaLogic/silent-failure-prevention.git",
        demo_command=("stability-demo",),
        demo_markers=("Overall Verdict: FAIL", "Gold refresh BLOCKED"),
        proof_paths=(
            "README.md",
            "notebooks/04_stability_deep_dive.py",
            "notebooks/05_free_edition_validation.py",
            "docs/technical-approach.md",
        ),
        expected_outcome="Intentionally blocks the publication path because the sample load is drifted.",
    ),
    Chapter(
        slug="measurable-control-effectiveness",
        title="Chapter 3: Measurable Control Effectiveness",
        repo_url="https://github.com/Org-EthereaLogic/measurable-control-effectiveness.git",
        demo_command=("benchmark-demo", "--seed", "42", "--rows", "1000"),
        demo_markers=("Overall Verdict: PASS",),
        evidence_command=(
            "benchmark-demo",
            "--seed",
            "42",
            "--rows",
            "1000",
            "--evidence-dir",
            "runs",
        ),
        evidence_paths=("runs/bench_42_1000.json",),
        proof_paths=("README.md", "docs/technical-approach.md"),
        expected_outcome="Ends in PASS and writes a machine-readable evidence bundle under runs/.",
    ),
)


def log(message: str) -> None:
    print(f"[executive-mode] {message}")


def run_command(
    command: list[str],
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    log(f"$ {shlex.join(command)}")
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {shlex.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result


def command_path(name: str) -> Optional[str]:
    return shutil.which(name)


def python_version(command: str) -> Optional[tuple[int, int, int]]:
    result = run_command(
        [command, "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"]
    )
    if result.returncode != 0:
        return None
    parts = result.stdout.strip().split(".")
    if len(parts) < 3:
        return None
    return tuple(int(part) for part in parts[:3])


def version_string(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def supported_python_candidates() -> list[str]:
    raw_candidates = [
        os.environ.get("EXECUTIVE_MODE_PYTHON", ""),
        "/opt/homebrew/bin/python3.13",
        "python3.13",
        "/opt/homebrew/bin/python3.12",
        "python3.12",
        "/opt/homebrew/bin/python3.11",
        "python3.11",
        "/opt/homebrew/bin/python3.10",
        "python3.10",
        "python3",
        "python",
    ]
    seen: set[str] = set()
    candidates: list[str] = []
    for candidate in raw_candidates:
        if candidate and candidate not in seen:
            candidates.append(candidate)
            seen.add(candidate)
    return candidates


def install_python_with_brew() -> None:
    brew = command_path("brew") or "/opt/homebrew/bin/brew"
    brew_path = Path(brew)
    if not brew_path.exists() and not command_path("brew"):
        raise RuntimeError(
            "No supported Python 3.10+ runtime found and Homebrew is unavailable."
        )
    run_command([brew, "install", "python@3.12"], check=True)


def find_supported_python(auto_install: bool) -> tuple[str, str, bool]:
    for candidate in supported_python_candidates():
        resolved = candidate if Path(candidate).exists() else command_path(candidate)
        if not resolved:
            continue
        version = python_version(resolved)
        if version and version >= (3, 10, 0):
            return resolved, version_string(version), False

    if not auto_install:
        raise RuntimeError(
            "No supported Python 3.10+ runtime found. Install python@3.12 or set "
            "EXECUTIVE_MODE_PYTHON."
        )

    log("No supported Python found; attempting Homebrew install of python@3.12.")
    install_python_with_brew()

    for candidate in supported_python_candidates():
        resolved = candidate if Path(candidate).exists() else command_path(candidate)
        if not resolved:
            continue
        version = python_version(resolved)
        if version and version >= (3, 10, 0):
            return resolved, version_string(version), True

    raise RuntimeError("Homebrew install completed, but no supported Python 3.10+ was found.")


def ensure_repo(chapter: Chapter, refresh: bool) -> None:
    if chapter.slug == "trusted-source-intake":
        return
    if chapter.path.exists():
        git_dir = chapter.path / ".git"
        if not git_dir.exists():
            raise RuntimeError(f"{chapter.path} exists but is not a git repository.")
        if refresh:
            run_command(["git", "pull", "--ff-only"], cwd=chapter.path, check=True)
        return
    run_command(["git", "clone", chapter.repo_url, chapter.slug], cwd=WORKSPACE_ROOT, check=True)


def ensure_environment(chapter: Chapter, python_cmd: str, rebuild: bool) -> None:
    venv_dir = chapter.path / ".venv"
    if rebuild and venv_dir.exists():
        shutil.rmtree(venv_dir)

    venv_python = chapter.venv_bin / "python"
    if not venv_python.exists():
        run_command([python_cmd, "-m", "venv", ".venv"], cwd=chapter.path, check=True)

    run_command(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        cwd=chapter.path,
        check=True,
    )
    run_command(
        [str(venv_python), "-m", "pip", "install", "-e", ".[dev]"],
        cwd=chapter.path,
        check=True,
    )


def proof_paths_ok(chapter: Chapter) -> bool:
    return all((chapter.path / rel_path).exists() for rel_path in chapter.proof_paths)


def run_guided_demo(chapter: Chapter) -> SurfaceResult:
    demo_executable = chapter.venv_bin / chapter.demo_command[0]
    if not demo_executable.exists():
        return SurfaceResult(
            status="FAIL",
            summary=f"Missing demo executable: {demo_executable.name}",
            command=" ".join(chapter.demo_command),
        )

    demo_command = [str(demo_executable), *chapter.demo_command[1:]]
    demo_result = run_command(demo_command, cwd=chapter.path)
    if demo_result.returncode != 0:
        return SurfaceResult(
            status="FAIL",
            summary="Guided demo command failed.",
            command=shlex.join(demo_command),
            stdout=demo_result.stdout,
            stderr=demo_result.stderr,
        )

    missing_markers = [marker for marker in chapter.demo_markers if marker not in demo_result.stdout]
    if missing_markers:
        return SurfaceResult(
            status="FAIL",
            summary=f"Guided demo ran, but expected output markers were missing: {missing_markers}",
            command=shlex.join(demo_command),
            stdout=demo_result.stdout,
            stderr=demo_result.stderr,
        )

    combined_stdout = demo_result.stdout
    combined_stderr = demo_result.stderr
    evidence_summary = ""

    if chapter.evidence_command:
        evidence_executable = chapter.venv_bin / chapter.evidence_command[0]
        evidence_command = [str(evidence_executable), *chapter.evidence_command[1:]]
        evidence_result = run_command(evidence_command, cwd=chapter.path)
        combined_stdout += "\n\n" + evidence_result.stdout
        combined_stderr += "\n\n" + evidence_result.stderr
        if evidence_result.returncode != 0:
            return SurfaceResult(
                status="FAIL",
                summary="Evidence command failed.",
                command=shlex.join(evidence_command),
                stdout=combined_stdout,
                stderr=combined_stderr,
            )
        missing_paths = [
            rel_path for rel_path in chapter.evidence_paths if not (chapter.path / rel_path).exists()
        ]
        if missing_paths:
            return SurfaceResult(
                status="FAIL",
                summary=f"Evidence command ran, but expected files were missing: {missing_paths}",
                command=shlex.join(evidence_command),
                stdout=combined_stdout,
                stderr=combined_stderr,
            )
        evidence_summary = " Evidence bundle created successfully."

    return SurfaceResult(
        status="PASS",
        summary=f"Guided demo completed. {chapter.expected_outcome}{evidence_summary}",
        command=shlex.join(demo_command),
        stdout=combined_stdout,
        stderr=combined_stderr,
    )


def probe_databricks(chapter: Chapter) -> SurfaceResult:
    if not chapter.databricks_bundle:
        return SurfaceResult(status="N/A", summary="This chapter does not require a live Databricks probe.")

    databricks_cmd = command_path("databricks")
    cfg_path = Path.home() / ".databrickscfg"
    if not databricks_cmd:
        return SurfaceResult(
            status="BLOCKED",
            summary="Databricks CLI is not installed on this machine.",
        )
    if not cfg_path.exists():
        return SurfaceResult(
            status="BLOCKED",
            summary="Databricks CLI is installed, but ~/.databrickscfg is missing.",
            command="databricks bundle validate --target dev",
        )

    validate_command = [databricks_cmd, "bundle", "validate", "--target", "dev"]
    result = run_command(validate_command, cwd=chapter.path)
    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode == 0:
        status = "PASS"
        summary = "Databricks bundle validation succeeded."
    elif "${workspace.host}" in output:
        status = "BLOCKED"
        summary = "Databricks CLI is present, but workspace.host is not configured for this target."
    else:
        status = "FAIL"
        summary = "Databricks bundle validation failed."
    return SurfaceResult(
        status=status,
        summary=summary,
        command=shlex.join(validate_command),
        stdout=result.stdout,
        stderr=result.stderr,
    )


def acquire_open_result(chapter: Chapter) -> SurfaceResult:
    if chapter.readme.exists() and proof_paths_ok(chapter):
        return SurfaceResult(
            status="PASS",
            summary="Repository, README, and executive proof files are present.",
        )
    return SurfaceResult(
        status="FAIL",
        summary="One or more required repository surfaces are missing.",
    )


def tail_snippet(text: str, max_lines: int = 16) -> str:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return ""
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])


def build_markdown_report(
    results: list[ChapterResult],
    runtime_python: str,
    runtime_version: str,
    python_installed: bool,
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    git_version = run_command(["git", "--version"]).stdout.strip()
    launcher_python = sys.executable
    launcher_version = "{}.{}.{}".format(*sys.version_info[:3])

    lines = [
        "# Executive Mode Report",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Workspace: `{WORKSPACE_ROOT}`",
        f"- Launcher Python: `{launcher_python}` (`{launcher_version}`)",
        f"- Runtime Python: `{runtime_python}` (`{runtime_version}`)",
        f"- Runtime installed during this run: `{python_installed}`",
        f"- Git: `{git_version}`",
        "",
        "## Portfolio Verdict",
        "",
        "The executive path is healthy when each chapter is cloneable, runnable via",
        "its repo-local environment, and explicit about whether Databricks access is",
        "available on the current machine.",
        "",
    ]

    for item in results:
        chapter = item.chapter
        lines.extend([
            f"## {chapter.title}",
            "",
            f"- Acquire/Open: `{item.acquire_open.status}` — {item.acquire_open.summary}",
            f"- Guided Demo: `{item.guided_demo.status}` — {item.guided_demo.summary}",
            f"- Databricks Surface: `{item.databricks_surface.status}` — {item.databricks_surface.summary}",
            "",
            "Proof files:",
        ])
        for rel_path in chapter.proof_paths:
            lines.append(f"- `{chapter.slug}/{rel_path}`")
        if chapter.evidence_paths:
            lines.append("")
            lines.append("Evidence files:")
            for rel_path in chapter.evidence_paths:
                lines.append(f"- `{chapter.slug}/{rel_path}`")
        if item.guided_demo.command:
            lines.extend(["", f"Demo command: `{item.guided_demo.command}`"])
        guided_snippet = tail_snippet(item.guided_demo.stdout)
        if guided_snippet:
            lines.extend(["", "Demo output excerpt:", "```text", guided_snippet, "```"])
        databricks_snippet = tail_snippet(item.databricks_surface.stdout or item.databricks_surface.stderr)
        if databricks_snippet:
            lines.extend(["", "Databricks output excerpt:", "```text", databricks_snippet, "```"])
        lines.append("")

    lines.extend([
        "## Notes",
        "",
        "- Guided demo success is reported separately from live Databricks access.",
        "- Chapter 2 is expected to end in `FAIL` because the checked-in drifted sample is designed to block Gold publication.",
        "- Re-run this report with `python3 scripts/executive_mode.py all --open-report` from Chapter One.",
        "",
    ])

    return "\n".join(lines)


def build_html_report(markdown_report: str) -> str:
    lines = markdown_report.splitlines()
    html_lines = [
        "<!doctype html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='utf-8'>",
        "  <title>Executive Mode Report</title>",
        "  <style>",
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem auto; max-width: 960px; line-height: 1.5; color: #1d1d1f; }",
        "    code, pre { font-family: 'SFMono-Regular', Menlo, monospace; }",
        "    pre { background: #f5f5f7; padding: 1rem; border-radius: 8px; overflow-x: auto; }",
        "    h1, h2 { color: #111827; }",
        "    ul { padding-left: 1.25rem; }",
        "  </style>",
        "</head>",
        "<body>",
    ]

    in_code_block = False
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("```"):
            close_list()
            if not in_code_block:
                html_lines.append("<pre><code>")
                in_code_block = True
            else:
                html_lines.append("</code></pre>")
                in_code_block = False
            continue
        if in_code_block:
            html_lines.append(html.escape(line))
            continue
        if line.startswith("# "):
            close_list()
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            close_list()
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(line[2:])}</li>")
        elif line == "":
            close_list()
        else:
            close_list()
            html_lines.append(f"<p>{html.escape(line)}</p>")

    close_list()
    if in_code_block:
        html_lines.append("</code></pre>")
    html_lines.extend(["</body>", "</html>"])
    return "\n".join(line for line in html_lines if line)


def write_reports(markdown_report: str) -> None:
    REPORT_MD.write_text(markdown_report, encoding="utf-8")
    REPORT_HTML.write_text(build_html_report(markdown_report), encoding="utf-8")


def open_report() -> None:
    if command_path("open"):
        run_command(["open", str(REPORT_HTML)])


def run_preflight(auto_install_python: bool) -> tuple[str, str, bool]:
    runtime_python, runtime_version, python_installed = find_supported_python(
        auto_install=auto_install_python
    )
    log(f"Using runtime Python {runtime_version} at {runtime_python}")
    return runtime_python, runtime_version, python_installed


def run_all(args: argparse.Namespace) -> int:
    runtime_python, runtime_version, python_installed = run_preflight(
        auto_install_python=args.auto_install_python
    )

    results: list[ChapterResult] = []

    for chapter in CHAPTERS:
        log(f"Preparing {chapter.title}")
        ensure_repo(chapter, refresh=args.refresh_clones)
        ensure_environment(chapter, runtime_python, rebuild=args.rebuild_venvs)

        acquire = acquire_open_result(chapter)
        guided_demo = run_guided_demo(chapter)
        databricks_surface = probe_databricks(chapter)
        results.append(
            ChapterResult(
                chapter=chapter,
                acquire_open=acquire,
                guided_demo=guided_demo,
                databricks_surface=databricks_surface,
            )
        )

    markdown_report = build_markdown_report(
        results,
        runtime_python=runtime_python,
        runtime_version=runtime_version,
        python_installed=python_installed,
    )
    write_reports(markdown_report)
    log(f"Wrote {REPORT_MD}")
    log(f"Wrote {REPORT_HTML}")

    if args.open_report:
        open_report()

    failing = [
        item for item in results
        if item.acquire_open.status == "FAIL"
        or item.guided_demo.status == "FAIL"
    ]
    return 1 if failing else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the portfolio executive mode workflow.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    all_parser = subparsers.add_parser("all", help="Clone, bootstrap, demo, and report.")
    all_parser.add_argument(
        "--auto-install-python",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Install python@3.12 with Homebrew if no supported Python is found.",
    )
    all_parser.add_argument(
        "--refresh-clones",
        action="store_true",
        help="Run git pull --ff-only in chapter repositories that already exist.",
    )
    all_parser.add_argument(
        "--rebuild-venvs",
        action="store_true",
        help="Delete and recreate each repo-local virtual environment.",
    )
    all_parser.add_argument(
        "--open-report",
        action="store_true",
        help="Open the generated HTML report after the run finishes.",
    )

    preflight_parser = subparsers.add_parser("preflight", help="Only verify runtime prerequisites.")
    preflight_parser.add_argument(
        "--auto-install-python",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Install python@3.12 with Homebrew if no supported Python is found.",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "all"

    if command == "preflight":
        runtime_python, runtime_version, python_installed = run_preflight(
            auto_install_python=args.auto_install_python
        )
        payload = {
            "runtime_python": runtime_python,
            "runtime_version": runtime_version,
            "python_installed": python_installed,
        }
        print(json.dumps(payload, indent=2))
        return 0

    return run_all(args)


if __name__ == "__main__":
    raise SystemExit(main())
