#!/usr/bin/env bash
# Run the same checks as CI / pre-commit (ruff, basedpyright, pytest).
# Usage: from repo root — make check   or   bash scripts/check.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

run_checks() {
  python -m ruff check .
  python -m basedpyright
  python -m pytest
}

if command -v uv >/dev/null 2>&1; then
  # Resolves the project env (creates .venv / syncs deps if needed).
  uv run --extra dev python -m ruff check .
  uv run --extra dev python -m basedpyright
  uv run --extra dev python -m pytest
  exit 0
fi

if [[ -d .venv ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/.venv/bin/activate"
fi

if ! python -c "import bling_jwt_auth" 2>/dev/null; then
  echo "error: bling_jwt_auth not importable — run: uv sync --extra dev" >&2
  echo "   (or: pip install -e '.[dev]')" >&2
  exit 1
fi

run_checks
