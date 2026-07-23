#!/bin/bash
set -e

echo "=== Veterinaria V2 - Reset Databases ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load DB connection info from docker-compose defaults
CORE_DB_CONTAINER="vet-core-db"
COMMUNITY_DB_CONTAINER="vet-community-db"
DB_USER="veterinaria_v2"
CORE_DB="core_db"
COMMUNITY_DB="community_db"

echo "Clearing core_db..."
docker exec "$CORE_DB_CONTAINER" psql -U "$DB_USER" -d "$CORE_DB" -c \
  "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo "Clearing community_db..."
docker exec "$COMMUNITY_DB_CONTAINER" psql -U "$DB_USER" -d "$COMMUNITY_DB" -c \
  "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Running migrations..."
cd "$PROJECT_ROOT"
bash scripts/migrate.sh

echo "=== Databases reset complete (schema cleared + migrations applied) ==="
