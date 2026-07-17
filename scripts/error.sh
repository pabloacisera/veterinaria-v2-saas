#!/bin/bash
set -e

ERRORS_FILE="docs/errors/errors.log.json"

get_next_id() {
    local last_num
    last_num=$(python3 -c "
import json
with open('$ERRORS_FILE') as f:
    data = json.load(f)
if not data:
    print('0')
else:
    ids = [e.get('id', 'ERR-000') for e in data]
    nums = [int(i.split('-')[1]) for i in ids]
    print(max(nums))
")
    printf "ERR-%03d" $((10#$last_num + 1))
}

case "${1:-}" in
    nuevo)
        if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
            echo "Usage: $0 nuevo \"módulo\" \"descripción del error\""
            exit 1
        fi
        ID=$(get_next_id)
        FECHA=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

        python3 -c "
import json, sys
with open('$ERRORS_FILE') as f:
    data = json.load(f)
data.append({
    'id': '$ID',
    'fecha': '$FECHA',
    'modulo': '$2',
    'descripcion': '$3',
    'detalle': '',
    'severidad': 'media',
    'estado': 'abierto',
    'tarea_asociada': ''
})
with open('$ERRORS_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
        echo "Created $ID in $ERRORS_FILE"
        ;;
    listar)
        python3 -c "
import json
with open('$ERRORS_FILE') as f:
    data = json.load(f)
if not data:
    print('No errors registered.')
else:
    print('Registered errors:')
    print()
    for e in data:
        print(f\"  {e.get('id', '???'):12s} [{e.get('estado', '?'):18s}] {e.get('modulo', '?'):20s} {e.get('descripcion', '')}\")
"
        ;;
    *)
        echo "Usage: $0 {nuevo|listar}"
        echo ""
        echo "  $0 nuevo \"módulo\" \"descripción\"    - Registrar un error"
        echo "  $0 listar                           - Listar todos los errores"
        exit 1
        ;;
esac
