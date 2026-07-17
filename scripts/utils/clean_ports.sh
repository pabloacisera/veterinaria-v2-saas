#!/bin/bash

# Lista de puertos definidos en tu docker-compose
PORTS=(5444 5435 6379 5672 15672 8000 3000 5173 5172)
echo "--- Iniciando limpieza de puertos ---"

for PORT in "${PORTS[@]}"; do
    PID=$(sudo lsof -t -i:"$PORT")

    if [ -z "$PID" ]; then
        echo "Puerto $PORT: Libre."
    else
        echo "Puerto $PORT: Ocupado por PID $PID. Intentando cerrar..."
        sudo kill -9 $PID
        
        # Pausa breve para asegurar que el sistema libere el puerto
        sleep 1
    fi
done

echo "--- Verificación final ---"
ALL_CLEAN=true
for PORT in "${PORTS[@]}"; do
    if sudo lsof -i:"$PORT" > /dev/null; then
        echo "¡Error! El puerto $PORT sigue ocupado."
        ALL_CLEAN=false
    fi
done

if [ "$ALL_CLEAN" = true ]; then
    echo "¡Listo! Todos los puertos están libres. Puedes ejecutar docker compose."
else
    echo "Algunos puertos no pudieron ser liberados. Por favor, revisa manualmente con 'sudo lsof -i :<puerto>'."
fi
