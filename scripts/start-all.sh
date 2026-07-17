#!/bin/bash
# start-all.sh — Levanta backend, frontend y tunnel para desarrollo local.
# Requiere que la infra (DBs, Redis, RabbitMQ) ya esté corriendo (make up).
#
# Problemas que resuelve esta versión:
#   - uvicorn se invoca desde el venv del backend con ruta explícita,
#     sin depender de que el venv esté activado en el shell del llamador.
#   - Los procesos en background se lanzan con la raíz del proyecto como
#     cwd, evitando que un `cd` fallido deje el contexto en un directorio
#     incorrecto para el siguiente paso.
#   - set -e se elimina del scope global para que un fallo en un proceso
#     de background no aborte el script antes de registrar los demás PIDs.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

VENV_UVICORN="$PROJECT_ROOT/backend/.venv/bin/uvicorn"

echo "=== Veterinaria V2 - Start All ==="
echo "  Project root: $PROJECT_ROOT"

# --- Validaciones previas ---
if [ ! -f "$VENV_UVICORN" ]; then
    echo ""
    echo "ERROR: uvicorn no encontrado en $VENV_UVICORN"
    echo "  Creá el entorno virtual primero:"
    echo "    cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo ""
    echo "ERROR: node_modules no encontrado en frontend/"
    echo "  Instalá las dependencias primero:"
    echo "    cd frontend && npm install"
    exit 1
fi

# --- Infra ---
echo ""
echo "1. Starting infrastructure..."
bash "$SCRIPT_DIR/dev-up.sh"

# --- Backend ---
echo ""
echo "2. Starting backend (uvicorn from venv)..."
(cd "$PROJECT_ROOT/backend" && "$VENV_UVICORN" src.main:app \
    --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

# --- Frontend ---
echo ""
echo "3. Starting frontend (npm run dev)..."
(cd "$PROJECT_ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

# --- Tunnel ---
echo ""
echo "4. Starting tunnel..."
bash "$SCRIPT_DIR/start-tunnel.sh" &
TUNNEL_PID=$!

echo ""
echo "=== All services started ==="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo "  Tunnel:   https://dev-api.artisandevs.site"
echo ""
echo "  PIDs — backend: $BACKEND_PID | frontend: $FRONTEND_PID | tunnel: $TUNNEL_PID"
echo ""
echo "Press Ctrl+C to stop all services"

cleanup() {
    echo ""
    echo "Stopping services..."
    kill "$BACKEND_PID" "$FRONTEND_PID" "$TUNNEL_PID" 2>/dev/null
    wait "$BACKEND_PID" "$FRONTEND_PID" "$TUNNEL_PID" 2>/dev/null
    echo "Done."
}

trap cleanup SIGINT SIGTERM
wait
