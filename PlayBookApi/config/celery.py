from PlayBookApi.environment import env

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270
CELERY_RESULT_EXTENDED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Initial seed schedule (synced to PeriodicTask via `seed_periodic_tasks` mgmt cmd
# in Fase 4. Keys are the canonical names of the Beat entries.)
CELERY_BEAT_SCHEDULE = {
    "markets-refresh-upcoming": {
        "task": "markets.tasks.refresh_upcoming_events",
        "schedule": 30 * 60.0,           # every 30 min
    },
    "markets-refresh-finished": {
        "task": "markets.tasks.refresh_finished_events",
        "schedule": 5 * 60.0,            # every 5 min
    },
    "predictions-generate": {
        "task": "predictions.tasks.generate_predictions",
        "schedule": 15 * 60.0,           # every 15 min
    },
    "predictions-settle": {
        "task": "predictions.tasks.settle_predictions",
        "schedule": 5 * 60.0,            # every 5 min
    },
}
