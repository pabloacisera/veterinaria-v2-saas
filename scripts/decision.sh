#!/bin/bash
set -e

DECISIONS_DIR="docs/decisions"

get_next_id() {
    local last_num
    last_num=$(ls "$DECISIONS_DIR"/ADR-*.json 2>/dev/null | sort | tail -1 | grep -oP '\d{3}' || echo "0")
    printf "ADR-%03d" $((10#$last_num + 1))
}

case "${1:-}" in
    nueva)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 nueva \"Título de la decisión\""
            exit 1
        fi
        ID=$(get_next_id)
        FECHA=$(date +%Y-%m-%d)
        FILE="$DECISIONS_DIR/$ID.json"

        cat > "$FILE" << EOF
{
  "id": "$ID",
  "fecha": "$FECHA",
  "titulo": "$2",
  "estado": "propuesta",
  "contexto": "",
  "decision": "",
  "consecuencias": [],
  "alternativas": [],
  "actores": ["@opencode"]
}
EOF
        echo "Created $FILE"
        echo "Open it in your editor to fill in the details."
        ;;
    listar)
        echo "Decisiones de Arquitectura:"
        echo ""
        for f in "$DECISIONS_DIR"/ADR-*.json; do
            id=$(grep -oP '"id":\s*"\K[^"]+' "$f")
            titulo=$(grep -oP '"titulo":\s*"\K[^"]+' "$f")
            estado=$(grep -oP '"estado":\s*"\K[^"]+' "$f")
            echo "  $id [$estado] $titulo"
        done
        ;;
    *)
        echo "Usage: $0 {nueva|listar}"
        echo ""
        echo "  $0 nueva \"Título\"    - Crear nuevo ADR"
        echo "  $0 listar             - Listar todos los ADRs"
        exit 1
        ;;
esac
