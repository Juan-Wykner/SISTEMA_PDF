#!/bin/sh
set -e

# Wait for database to be available (if using PostgreSQL)
if [ "$DATABASE_URL" ]; then
    echo "Aguardando banco de dados..."
    DB_HOST=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(u.hostname or 'localhost')
PY
)
    DB_PORT=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(u.port or 5432)
PY
)
    DB_USER=$(python - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(u.username or 'postgres')
PY
)
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" 2>/dev/null; do
      sleep 1
    done
fi

# Run migrations
echo "Executando migrações..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

echo "Iniciando aplicação..."
exec "$@"
