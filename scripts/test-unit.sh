#!/bin/bash
set -e

echo "=== Running Unit Tests ==="

cd backend
export PYTHONPATH=.
if [ -f ".venv/bin/pytest" ]; then
    .venv/bin/pytest src/tests/unit src/domain/tests -v --tb=short "$@"
else
    pytest src/tests/unit src/domain/tests -v --tb=short "$@"
fi

echo "=== Unit tests complete ==="
