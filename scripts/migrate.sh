#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Running Database Migrations ==="

echo "--- core_db ---"
if [ -f "$PROJECT_ROOT/backend/.venv/bin/alembic" ]; then
    (cd "$PROJECT_ROOT/backend" && .venv/bin/alembic upgrade head)
elif command -v alembic &> /dev/null; then
    (cd "$PROJECT_ROOT/backend" && alembic upgrade head)
else
    echo "WARNING: Alembic not found. Init scripts will run via Docker entrypoint."
    echo "Restart core_db to re-run init scripts: docker compose restart core_db"
fi

echo "--- community_db ---"
if [ -f "$PROJECT_ROOT/backend/.venv/bin/alembic" ]; then
    (cd "$PROJECT_ROOT/backend" && .venv/bin/alembic -c community_alembic.ini upgrade head)
elif command -v alembic &> /dev/null; then
    (cd "$PROJECT_ROOT/backend" && alembic -c community_alembic.ini upgrade head)
else
    echo "WARNING: Alembic not found for community_db. Init scripts handle this on first startup."
fi

echo "=== Migrations complete ==="
