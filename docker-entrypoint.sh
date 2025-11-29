#!/bin/bash

# Wait for database to be available (if using PostgreSQL)
if [ "$DATABASE_URL" ]; then
    echo "Aguardando banco de dados..."
    while ! pg_isready -h db -p 5432 -U postgres 2>/dev/null; do
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