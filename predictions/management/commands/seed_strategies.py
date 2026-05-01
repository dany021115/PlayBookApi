"""Idempotent seed for the 4 default Strategy rows."""

from django.core.management.base import BaseCommand

from predictions.models import Strategy


SEED = [
    {
        "name": "value_bet",
        "type": Strategy.Type.VALUE_BET,
        "description": "Detecta cuotas con margen positivo (edge) sobre el consenso del mercado.",
        "params": {"min_edge": 0.0},
    },
    {
        "name": "form_streak",
        "type": Strategy.Type.FORM_STREAK,
        "description": "Apuesta cuando un equipo lleva una racha clara de victorias en sus últimos 5 partidos.",
        "params": {"min_wins": 4, "min_price": 1.7},
    },
    {
        "name": "totals_consensus",
        "type": Strategy.Type.TOTALS_CONSENSUS,
        "description": "Sugiere over/under según el promedio de goles de ambos equipos en últimos 10 partidos.",
        "params": {"over_threshold": 2.8, "under_threshold": 2.0, "line": 2.5},
    },
    {
        "name": "llm_only",
        "type": Strategy.Type.LLM_ONLY,
        "description": "Solo el LLM decide la apuesta y la justificación, usando todo el contexto disponible.",
        "params": {"min_confidence": 65},
    },
]


class Command(BaseCommand):
    help = "Seed the four default Strategy rows (idempotent)."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in SEED:
            obj, was_created = Strategy.objects.update_or_create(
                name=entry["name"],
                defaults={
                    "type": entry["type"],
                    "description": entry["description"],
                    "params": entry["params"],
                    "enabled": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"seed_strategies: created={created} updated={updated} total={Strategy.objects.count()}"
        ))
