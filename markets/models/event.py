from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Event(TimeStamped):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        LIVE = "live", "Live"
        FINISHED = "finished", "Finished"
        POSTPONED = "postponed", "Postponed"
        CANCELED = "canceled", "Canceled"

    upstream_id = models.IntegerField(unique=True, db_index=True,
                                      help_text="Event id from sports-odds-api.")
    league = models.ForeignKey("markets.League", on_delete=models.CASCADE, related_name="events")
    home_team = models.ForeignKey("markets.Team", on_delete=models.PROTECT, related_name="home_events")
    away_team = models.ForeignKey("markets.Team", on_delete=models.PROTECT, related_name="away_events")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    start_time = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    minute = models.CharField(max_length=24, blank=True, default="")
    upstream_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "start_time"]),
            models.Index(fields=["league", "start_time"]),
        ]
        ordering = ["start_time"]

    def __str__(self) -> str:
        return f"{self.home_team} vs {self.away_team} ({self.status})"
