#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ALEMBIC_BIN="$PROJECT_ROOT/backend/.venv/bin/alembic"

echo "=== Running Database Migrations ==="

echo "--- core_db ---"
if [ -f "$ALEMBIC_BIN" ]; then
    cd "$PROJECT_ROOT/backend" && .venv/bin/alembic upgrade head
elif command -v alembic &> /dev/null; then
    cd "$PROJECT_ROOT/backend" && alembic upgrade head
else
    echo "ERROR: Alembic not found. Install with: cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "--- community_db ---"
if [ -f "$ALEMBIC_BIN" ]; then
    cd "$PROJECT_ROOT/backend" && .venv/bin/alembic -c community_alembic.ini upgrade head
elif command -v alembic &> /dev/null; then
    cd "$PROJECT_ROOT/backend" && alembic -c community_alembic.ini upgrade head
else
    echo "ERROR: Alembic not found for community_db."
    exit 1
fi

echo "=== Migrations complete ==="
