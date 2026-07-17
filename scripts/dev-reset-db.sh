#!/bin/bash
set -e

echo "=== Veterinaria V2 - Reset Databases ==="

echo "Stopping database containers..."
docker compose stop core_db community_db

echo "Removing volumes..."
docker compose rm -f core_db community_db
docker volume rm veter_v2_core_db_data veter_v2_community_db_data 2>/dev/null || true

echo "Starting fresh databases..."
docker compose up -d core_db community_db

echo "Waiting for databases to be healthy..."
sleep 3

echo "Running migrations..."
bash scripts/migrate.sh

echo "=== Databases reset complete ==="
