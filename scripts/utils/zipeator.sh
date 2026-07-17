#!/bin/bash
echo "Definiendo directorios..."
# Guardamos la ubicación actual para volver después
original_dir=$(pwd)

output_zip="scripts/app.zip"
# Definimos los directorios a excluir
excludes=("node_modules/*" "venv/*" ".git/*" "__pycache__/*")

# Construimos los argumentos
exclude_args=""
for item in "${excludes[@]}"; do
    exclude_args="$exclude_args -x $item"
done

echo "Empaquetando..."
# Comprimimos desde la raíz
zip -r "$output_zip" . $exclude_args

# Volvemos al directorio original
cd "$original_dir"

echo "Archivo $output_zip creado satisfactoriamente."
