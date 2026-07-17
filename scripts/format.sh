#!/bin/bash
set -e

echo "=== Running Formatters ==="

if command -v black &> /dev/null; then
    echo "--- Backend (black) ---"
    black backend/src/ backend/tests/
else
    echo "WARNING: black not found. Install it: pip install black"
fi

if command -v prettier &> /dev/null; then
    echo "--- Frontend (prettier) ---"
    prettier --write "frontend/src/**/*.{ts,tsx,js,jsx,json,css}"
else
    echo "WARNING: prettier not found."
fi

echo "=== Formatting complete ==="
