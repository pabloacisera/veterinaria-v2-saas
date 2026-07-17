#!/bin/bash
set -e

echo "=== Setting up git hooks ==="

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "WARNING: Not a git repository. Hooks not installed."
    exit 0
fi

cp "$REPO_ROOT/infra/githooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

echo "Pre-commit hook installed at .git/hooks/pre-commit"
echo "=== Git hooks setup complete ==="
