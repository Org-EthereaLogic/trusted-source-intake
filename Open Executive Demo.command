#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

pick_launcher_python() {
  local candidates=(
    "${EXECUTIVE_MODE_LAUNCHER_PYTHON:-}"
    python3.12
    python3.11
    python3.10
    python3
    python
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -n "$candidate" ]] && command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

PYTHON_CMD="$(pick_launcher_python)" || {
  echo "No Python interpreter is available."
  echo "Install Homebrew and python@3.12, then rerun this launcher."
  exit 1
}

exec "$PYTHON_CMD" "$ROOT/scripts/executive_mode.py" all --open-report "$@"
