#!/bin/bash
set -e

echo "=== Veterinaria V2 — Production Deploy (Nginx + Cloudflare Tunnel) ==="

# Verificar .env
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "  cp env.example .env && nano .env"
    exit 1
fi

echo "Validating environment..."
bash scripts/validate-env.sh

echo "Pulling latest images..."
git pull origin main

echo "Building and starting production stack (no Caddy, no cloudflared)..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build backend

echo "Waiting for backend health..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:4001/health > /dev/null 2>&1; then
        echo "  Backend is healthy on port 4001!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Backend failed to start within 30s"
        docker compose -f docker-compose.yml -f docker-compose.prod.yml logs backend --tail 50
        exit 1
    fi
    sleep 2
done

echo "Running migrations..."
echo "--- core_db ---"
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend alembic upgrade head
echo "--- community_db ---"
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend alembic -c community_alembic.ini upgrade head

echo "Building frontend (static files)..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend
sleep 5

echo "Copying frontend files to Nginx serving directory..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T frontend sh -c "cp -r /app/dist/. /opt/veter.v2/frontend/dist/"

echo "Reloading Nginx..."
docker exec nginx-global nginx -t && docker exec nginx-global nginx -s reload

echo "=== Deploy complete ==="
echo "Frontend: https://veterinaria.artisandevs.site"
echo "Backend: https://veterinaria.artisandevs.site/api/v1/health"
echo "Backend direct: http://localhost:4001/health"
