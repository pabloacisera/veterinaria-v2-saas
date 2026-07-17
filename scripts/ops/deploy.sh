#!/bin/bash
set -e

echo "=== Veterinaria V2 — Production Deploy ==="

ENV_EXAMPLE="env.example"
if [ ! -f "$ENV_EXAMPLE" ]; then
    ENV_EXAMPLE=".env.example"
fi
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Create it from $ENV_EXAMPLE"
    echo "  cp $ENV_EXAMPLE .env && nano .env"
    exit 1
fi

echo "Validating environment..."
bash scripts/validate-env.sh

echo "Pulling latest images..."
git pull origin main

echo "Building and starting production stack..."
docker compose --profile production up -d --build

echo "Waiting for backend health..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  Backend is healthy!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Backend failed to start within 30s"
        docker compose --profile production logs backend --tail 50
        exit 1
    fi
    sleep 2
done

echo "Running migrations..."
echo "--- core_db ---"
docker compose --profile production exec -T backend python -m alembic upgrade head
echo "--- community_db ---"
docker compose --profile production exec -T backend python -m alembic -c community_alembic.ini upgrade head

echo "=== Deploy complete ==="
echo "Frontend: https://dev-api.artisandevs.site"
echo "Backend: https://dev-api.artisandevs.site/health"
