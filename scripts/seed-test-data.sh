#!/bin/bash
set -e

echo "=== Seeding Test Data ==="
echo "NOTE: Requires backend to be running and migrations to be applied."

if [ -f "backend/.venv/bin/python" ]; then
    cd backend && PYTHONPATH=. .venv/bin/python -m src.infrastructure.seed
elif command -v python &> /dev/null; then
    cd backend && PYTHONPATH=. python -m src.infrastructure.seed
else
    echo "ERROR: Python not found."
    exit 1
fi

echo "=== Test data seeded ==="
