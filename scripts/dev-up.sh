#!/bin/bash
set -e

echo "=== Veterinaria V2 - Development Stack Up ==="

echo "Starting Docker Compose services..."
docker compose up -d core_db community_db redis rabbitmq

echo "Waiting for databases to be healthy..."

# Wait for PostgreSQL (core_db)
echo "  Waiting for core_db..."
until docker exec vet-core-db pg_isready -U veterinaria_v2 -d core_db >/dev/null 2>&1; do
    sleep 1
done
echo "  core_db ready"

# Wait for PostgreSQL (community_db)
echo "  Waiting for community_db..."
until docker exec vet-community-db pg_isready -U veterinaria_v2 -d community_db >/dev/null 2>&1; do
    sleep 1
done
echo "  community_db ready"

# Wait for Redis
echo "  Waiting for Redis..."
until docker exec vet-redis redis-cli ping >/dev/null 2>&1; do
    sleep 1
done
echo "  Redis ready"

# Wait for RabbitMQ AMQP port
echo "  Waiting for RabbitMQ..."
until docker exec vet-rabbitmq rabbitmqctl await_startup 2>/dev/null; do
    sleep 2
done
echo "  RabbitMQ ready"

echo "Running migrations..."
bash scripts/migrate.sh

echo "=== Stack is up ==="
echo "  core_db:      localhost:5444"
echo "  community_db: localhost:5435"
echo "  Redis:        localhost:6379"
echo "  RabbitMQ:     localhost:5672 (management: localhost:15672)"
