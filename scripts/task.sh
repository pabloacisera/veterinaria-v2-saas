#!/bin/bash
set -e

BACKLOG_FILE="docs/tasks/backlog.json"

get_next_id() {
    local last_id
    last_id=$(python3 -c "
import json
with open('$BACKLOG_FILE') as f:
    data = json.load(f)
ids = [t['id'] for t in data['tareas']]
nums = [int(i.split('-')[1]) for i in ids]
next_num = max(nums) + 1 if nums else 1
print(f'TASK-{next_num:03d}')
")
    echo "$last_id"
}

validate_schema() {
    if command -v check-json-schema &> /dev/null; then
        check-json-schema --schema "infra/githooks/schemas/backlog.schema.json" "$BACKLOG_FILE"
    elif command -v python3 &> /dev/null; then
        python3 -c "
import json, sys
with open('$BACKLOG_FILE') as f:
    data = json.load(f)
required = ['id', 'titulo', 'estado', 'prioridad', 'dependencias', 'decisiones_relacionadas', 'tests_relacionados']
for t in data['tareas']:
    for r in required:
        if r not in t:
            print(f'ERROR: {t.get(\"id\", \"?\")} missing field: {r}')
            sys.exit(1)
print('Schema OK')
"
    fi
}

case "${1:-}" in
    nueva)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 nueva \"Título de la tarea\""
            exit 1
        fi
        TITLE="$2"
        ID=$(get_next_id)
        python3 -c "
import json
with open('$BACKLOG_FILE') as f:
    data = json.load(f)
data['tareas'].append({
    'id': '$ID',
    'titulo': '$TITLE',
    'estado': 'pendiente',
    'prioridad': 'media',
    'asignado': '',
    'dependencias': [],
    'decisiones_relacionadas': [],
    'tests_relacionados': []
})
with open('$BACKLOG_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
        echo "Created $ID: $TITLE"
        validate_schema
        ;;
    cerrar)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 cerrar TASK-XXX"
            exit 1
        fi
        TASK_ID="$2"
        python3 -c "
import json, sys
with open('$BACKLOG_FILE') as f:
    data = json.load(f)
for t in data['tareas']:
    if t['id'] == '$TASK_ID':
        if not t.get('tests_relacionados'):
            print(f'ERROR: $TASK_ID no tiene tests_relacionados. No se puede cerrar.')
            sys.exit(1)
        if t['estado'] == 'completada':
            print(f'ERROR: $TASK_ID ya está completada.')
            sys.exit(1)
        t['estado'] = 'completada'
        break
else:
    print(f'ERROR: $TASK_ID no encontrada.')
    sys.exit(1)
with open('$BACKLOG_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
        echo "$TASK_ID marcada como completada"
        validate_schema
        ;;
    listar)
        python3 -c "
import json
with open('$BACKLOG_FILE') as f:
    data = json.load(f)
print(f\"Sprint: {data['sprint']}\")
print()
for t in data['tareas']:
    print(f\"  {t['id']:12s} [{t['estado']:12s}] {t['titulo']}\")
"
        ;;
    *)
        echo "Usage: $0 {nueva|cerrar|listar} [args]"
        echo ""
        echo "  $0 nueva \"Título\"        - Crear nueva tarea"
        echo "  $0 cerrar TASK-XXX       - Marcar tarea como completada"
        echo "  $0 listar                 - Listar todas las tareas"
        exit 1
        ;;
esac
