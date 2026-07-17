#!/bin/bash
set -e

echo "=== Veterinaria V2 - Development Stack Up ==="

echo "Starting Docker Compose services..."
docker compose up -d core_db community_db redis rabbitmq

echo "Waiting for databases to be healthy..."
sleep 3

echo "Running migrations..."
bash scripts/migrate.sh

echo "=== Stack is up ==="
echo "  core_db:      localhost:5444"
echo "  community_db: localhost:5435"
echo "  Redis:        localhost:6379"
echo "  RabbitMQ:     localhost:5672 (management: localhost:15672)"
