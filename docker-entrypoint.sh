#!/bin/sh
set -e
if [ "$DATABASE_URL" ]; then
  DB_HOST=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.hostname or 'localhost')
PY
)
  DB_PORT=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.port or 5432)
PY
)
  DB_USER=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.username or 'postgres')
PY
)
  while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" 2>/dev/null; do
    sleep 1
  done
fi
python manage.py migrate --noinput
exec "$@"
