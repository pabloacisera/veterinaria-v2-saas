#!/bin/bash
set -e

echo "=== Running Database Migrations ==="

echo "--- core_db ---"
if [ -f "backend/.venv/bin/alembic" ]; then
    cd backend && .venv/bin/alembic upgrade head
elif command -v alembic &> /dev/null; then
    cd backend && alembic upgrade head
else
    echo "WARNING: Alembic not found. Init scripts will run via Docker entrypoint."
    echo "Restart core_db to re-run init scripts: docker compose restart core_db"
fi

echo "--- community_db ---"
if [ -f "backend/.venv/bin/alembic" ]; then
    cd backend && .venv/bin/alembic -c community_alembic.ini upgrade head
elif command -v alembic &> /dev/null; then
    cd backend && alembic -c community_alembic.ini upgrade head
else
    echo "WARNING: Alembic not found for community_db. Init scripts handle this on first startup."
fi

echo "=== Migrations complete ==="
