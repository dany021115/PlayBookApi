#!/bin/bash
set -e

echo "==> Running migrations..."
uv run python manage.py migrate --noinput

echo "==> Creating superuser (if not exists)..."
uv run python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@playbook.local')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        username=email.split('@')[0],
        email=email,
        password=password,
    )
    print(f'Superuser {email} created.')
else:
    print(f'Superuser {email} already exists.')
"

echo "==> Seeding strategies (idempotent)..."
uv run python manage.py seed_strategies || echo "(seed_strategies command not yet available — skipping)"

echo "==> Seeding API keys (idempotent)..."
uv run python manage.py seed_api_keys || echo "(seed_api_keys command not yet available — skipping)"

echo "==> Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "==> Starting daphne (HTTP + WebSocket ASGI)..."
exec uv run daphne -b 0.0.0.0 -p 8000 --http-timeout 60 PlayBookApi.asgi:application
