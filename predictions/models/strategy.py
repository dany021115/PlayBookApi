from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Strategy(TimeStamped):
    class Type(models.TextChoices):
        VALUE_BET = "value_bet", "Value Bet"
        FORM_STREAK = "form_streak", "Form Streak"
        TOTALS_CONSENSUS = "totals_consensus", "Totals Consensus"
        LLM_ONLY = "llm_only", "LLM Only"

    name = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=32, choices=Type.choices)
    enabled = models.BooleanField(default=True)
    params = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name_plural = "Strategies"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
