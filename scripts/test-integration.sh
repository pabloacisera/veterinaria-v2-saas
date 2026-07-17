#!/bin/bash
set -e

echo "=== Running Integration Tests ==="

cd backend
if [ -f ".venv/bin/pytest" ]; then
    .venv/bin/pytest tests/integration -v --tb=short "$@"
else
    pytest tests/integration -v --tb=short "$@"
fi

echo "=== Integration tests complete ==="
