"""Idempotent seed of one client API key (for the Flutter app).

Usage:
    uv run python manage.py seed_api_keys
    uv run python manage.py seed_api_keys --name "PlayBook iOS" --print
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey


class Command(BaseCommand):
    help = "Create a default ClientAPIKey for the mobile app (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--name", default="PlayBook Flutter App")
        parser.add_argument("--print", action="store_true",
                            help="Force-print the secret key (default: only on first creation).")

    def handle(self, *args, name: str = "PlayBook Flutter App", **opts):
        existing = APIKey.objects.filter(name=name).first()
        if existing and not opts.get("print"):
            self.stdout.write(self.style.WARNING(
                f"APIKey '{name}' already exists (prefix={existing.prefix}). "
                f"Use --print to regenerate output (you cannot recover the secret if lost)."
            ))
            return
        if existing:
            self.stdout.write(self.style.WARNING(
                f"APIKey '{name}' exists. Cannot recover the secret — to rotate, delete + re-create."
            ))
            return
        api_key, key = APIKey.objects.create_key(name=name)
        self.stdout.write(self.style.SUCCESS(f"Created APIKey '{name}'"))
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("⚠️  SAVE THIS KEY NOW — it cannot be retrieved later:"))
        self.stdout.write(f"  X-Api-Key: {key}")
        self.stdout.write("")
        self.stdout.write("Use it in every request to /api/v1/*:")
        self.stdout.write(f'  curl -H "X-Api-Key: {key}" ...')
