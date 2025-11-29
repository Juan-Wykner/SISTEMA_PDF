#!/bin/sh
set -e

# Resolve DB connection details from DATABASE_URL or DB_* vars
RESOLVED_HOST=""
RESOLVED_PORT=""
RESOLVED_USER=""

if [ -n "$DATABASE_URL" ]; then
  RESOLVED_HOST=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.hostname or '')
PY
)
  RESOLVED_PORT=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.port or 5432)
PY
)
  RESOLVED_USER=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL',''))
print(u.username or 'postgres')
PY
)
else
  RESOLVED_HOST="${DB_HOST:-localhost}"
  RESOLVED_PORT="${DB_PORT:-5432}"
  RESOLVED_USER="${DB_USER:-postgres}"
fi

echo "Waiting for DB ${RESOLVED_HOST}:${RESOLVED_PORT} user=${RESOLVED_USER}"
until pg_isready -h "$RESOLVED_HOST" -p "$RESOLVED_PORT" -U "$RESOLVED_USER" 2>/dev/null; do
  sleep 1
done

python manage.py migrate --noinput
exec "$@"
