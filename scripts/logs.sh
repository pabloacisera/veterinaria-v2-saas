#!/bin/bash
set -e

SERVICE="${1:-all}"

echo "=== Logs for: $SERVICE ==="

case "$SERVICE" in
    core_db)
        docker compose logs -f --tail=100 core_db
        ;;
    community_db)
        docker compose logs -f --tail=100 community_db
        ;;
    redis)
        docker compose logs -f --tail=100 redis
        ;;
    rabbitmq)
        docker compose logs -f --tail=100 rabbitmq
        ;;
    backend)
        docker compose logs -f --tail=100 backend
        ;;
    frontend)
        docker compose logs -f --tail=100 frontend
        ;;
    caddy)
        docker compose logs -f --tail=100 caddy
        ;;
    all)
        docker compose logs -f --tail=50
        ;;
    *)
        echo "Usage: $0 [core_db|community_db|redis|rabbitmq|backend|frontend|caddy|all]"
        exit 1
        ;;
esac
