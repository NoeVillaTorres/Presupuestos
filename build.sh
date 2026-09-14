#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Si existe un disco de Render y no se ha copiado la base de datos todavía, copiarla:
if [ -d "$DATA_DIR" ] && [ ! -f "$DATA_DIR/db.sqlite3" ]; then
    echo "Copiando base de datos inicial al disco persistente..."
    cp db.sqlite3 "$DATA_DIR/db.sqlite3"
fi

python manage.py migrate