#!/usr/bin/env bash
# Static code review validations for Veterinaria V2
# Outputs markdown report to stdout
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

PASS=0
WARN=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
warn() { WARN=$((WARN + 1)); echo "  ⚠️ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "## 🔍 Static Review"
echo ""

# ── 1. Clean Architecture: backend domain/ must not import infrastructure/ or interfaces/ ──
echo "### 1. Clean Architecture (backend)"
VIOLATIONS=$(grep -rn "from src\.infrastructure\|from src\.interfaces\|import src\.infrastructure\|import src\.interfaces" \
  --include="*.py" backend/src/domain/ 2>/dev/null || true)
if [ -z "$VIOLATIONS" ]; then
  pass "domain/ has no imports from infrastructure/ or interfaces/"
else
  fail "domain/ imports from infrastructure/ or interfaces/:"
  echo "$VIOLATIONS" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 2. Clean Architecture: frontend shared/ must not import from higher layers ──
echo ""
echo "### 2. Clean Architecture (frontend)"
VIOLATIONS=$(grep -rn "from.*features/\|from.*widgets/\|from.*pages/\|from.*app/" \
  --include="*.ts" --include="*.tsx" frontend/src/shared/ 2>/dev/null || true)
if [ -z "$VIOLATIONS" ]; then
  pass "shared/ has no imports from features/, widgets/, pages/, or app/"
else
  warn "shared/ imports from higher layers (may be intentional):"
  echo "$VIOLATIONS" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 3. No secrets hardcoded ──
echo ""
echo "### 3. Hardcoded secrets"
SECRETS=$(grep -rn "sk-[a-zA-Z0-9]\{20,\}" \
  --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
  backend/src/ frontend/src/ 2>/dev/null | grep -v "test\|mock\|example\|placeholder" || true)
if [ -z "$SECRETS" ]; then
  pass "No hardcoded secrets detected"
else
  fail "Possible hardcoded secrets:"
  echo "$SECRETS" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 4. .env not committed ──
echo ""
echo "### 4. .env files"
ENV_FILES=$(git ls-files --cached | grep -E '\.env$|\.env\.' | grep -v 'env\.example' || true)
if [ -z "$ENV_FILES" ]; then
  pass "No .env files committed"
else
  fail ".env files found in git:"
  echo "$ENV_FILES" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 5. UUIDv7 usage (warn on uuid4) ──
echo ""
echo "### 5. UUIDv7 compliance"
UUID4=$(grep -rn "uuid4\|uuid\.uuid4" --include="*.py" backend/src/domain/ backend/src/infrastructure/ 2>/dev/null || true)
if [ -z "$UUID4" ]; then
  pass "No uuid4 usage in domain/ or infrastructure/"
else
  warn "uuid4 found (should use uuid7):"
  echo "$UUID4" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 6. Soft-delete: no destructive SQL in migrations ──
echo ""
echo "### 6. Destructive migrations"
DESTRUCTIVE=$(grep -rln "DELETE FROM\|DROP TABLE\|DROP COLUMN" \
  backend/alembic/versions/ backend/community_alembic/versions/ 2>/dev/null || true)
if [ -z "$DESTRUCTIVE" ]; then
  pass "No destructive SQL in migrations"
else
  warn "Destructive SQL found in migrations:"
  echo "$DESTRUCTIVE" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── 7. Tests present for modified source files ──
echo ""
echo "### 7. Test coverage"
MODIFIED_SRC=$(git diff --name-only main...HEAD 2>/dev/null | grep -E "^backend/src/(domain|application|infrastructure|interfaces)/.*\.py$" | grep -v __pycache__ || true)
if [ -n "$MODIFIED_SRC" ]; then
  HAS_TESTS=false
  while IFS= read -r file; do
    BASENAME=$(basename "$file" .py)
    if find backend/src/tests/ -name "*${BASENAME}*" 2>/dev/null | grep -q .; then
      HAS_TESTS=true
    fi
  done <<< "$MODIFIED_SRC"
  if [ "$HAS_TESTS" = true ]; then
    pass "Some modified source files have corresponding tests"
  else
    warn "Modified source files may lack test coverage"
  fi
else
  pass "No backend source files modified"
fi

# ── 8. docker-compose: no hardcoded ports ──
echo ""
echo "### 8. Docker Compose"
COMPOSE_ISSUES=$(grep -n "127\.0\.0\|0\.0\.0\.0:" docker-compose*.yml 2>/dev/null || true)
if [ -z "$COMPOSE_ISSUES" ]; then
  pass "No hardcoded bind addresses in docker-compose"
else
  warn "Hardcoded addresses found (may be intentional):"
  echo "$COMPOSE_ISSUES" | while IFS= read -r line; do echo "    \`$line\`"; done
fi

# ── Summary ──
echo ""
echo "---"
echo ""
echo "| Check | Result |"
echo "|-------|--------|"
echo "| Passed | $PASS |"
echo "| Warnings | $WARN |"
echo "| Failed | $FAIL |"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo "**Veredicto: ❌ FAIL** — $FAIL critical issues found"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  echo "**Veredicto: ⚠️ PASS with warnings** — $WARN items to review"
  exit 0
else
  echo "**Veredicto: ✅ PASS** — All checks passed"
  exit 0
fi
