#!/bin/sh
set -e

echo "Running core_db migrations..."
alembic upgrade head
echo "Core DB migrations complete."

echo "Running community_db migrations..."
alembic -c community_alembic.ini upgrade head
echo "Community DB migrations complete."

exec uvicorn src.main:app --host 0.0.0.0 --port 8000
