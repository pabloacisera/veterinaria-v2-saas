#!/bin/bash
set -e

echo "=== Running Linters ==="

if command -v ruff &> /dev/null; then
    echo "--- Backend (ruff) ---"
    ruff check backend/src/
else
    echo "WARNING: ruff not found. Install it: pip install ruff"
fi

if command -v eslint &> /dev/null; then
    echo "--- Frontend (eslint) ---"
    eslint frontend/src/
else
    echo "WARNING: eslint not found."
fi

echo "=== Linting complete ==="
