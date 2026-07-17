#!/bin/bash
set -e

echo "=== Running E2E Tests ==="

E2E_DIR="tests/e2e-full-stack"

if [ -f "$E2E_DIR/node_modules/.bin/playwright" ]; then
    cd "$E2E_DIR" && npx playwright test "$@"
else
    echo "WARNING: Playwright not found in $E2E_DIR. Installing..."
    cd "$E2E_DIR" && npm install && npx playwright install chromium
    npx playwright test "$@"
fi

echo "=== E2E tests complete ==="
