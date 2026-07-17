#!/bin/bash
set -e

echo "=== Veterinaria V2 - Start All ==="

echo "1. Starting infrastructure..."
bash scripts/dev-up.sh

echo "2. Starting backend..."
cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "3. Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo "4. Starting tunnel..."
bash scripts/start-tunnel.sh &
TUNNEL_PID=$!

echo ""
echo "=== All services started ==="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo "  Tunnel:   https://dev-api.artisandevs.site"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID $TUNNEL_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
