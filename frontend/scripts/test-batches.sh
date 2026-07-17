#!/bin/bash
# Batch test runner for frontend tests.
# Workaround for JSDOM environment overhead causing hangs with >20 test files.
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

ALL_FILES=()
while IFS= read -r f; do ALL_FILES+=("$f"); done < <(find src -name '*.test.ts' -o -name '*.test.tsx' -type f | sort)
TOTAL_FILES=${#ALL_FILES[@]}

FAILED_BATCHES=0

echo ":: Running $TOTAL_FILES test files in batches"
echo ""

BATCH_NUM=0
for ((i=0; i<TOTAL_FILES; i+=10)); do
    BATCH_NUM=$((BATCH_NUM + 1))
    BATCH=("${ALL_FILES[@]:i:10}")
    echo "--- Batch $BATCH_NUM ($((${#BATCH[@]})) files) ---"

    if npx vitest run --reporter=verbose --testTimeout=40000 "${BATCH[@]}" 2>&1; then
        echo "--- Batch $BATCH_NUM PASSED ---"
    else
        FAILED_BATCHES=$((FAILED_BATCHES + 1))
        echo "--- Batch $BATCH_NUM FAILED ---"
    fi
    echo ""
done

echo "==============================="
if [ "$FAILED_BATCHES" -eq 0 ]; then
    echo "All $TOTAL_FILES test files PASSED"
else
    echo "WARNING: $FAILED_BATCHES batch(es) had failures"
fi
echo "==============================="

exit $FAILED_BATCHES
