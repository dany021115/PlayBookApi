"""Environment loader. All settings funnel through `env(...)`."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_SECRET_KEY=(str, "django-insecure-change-me-in-production"),
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    LOG_LEVEL=(str, "INFO"),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    REDIS_URL=(str, "redis://127.0.0.1:6379/1"),
    CELERY_BROKER_URL=(str, "redis://127.0.0.1:6379/0"),
    # Sports-odds-api S2S
    SPORTS_ODDS_API_URL=(str, "http://sports-api:8000"),
    SPORTS_ODDS_JWT_KEYS=(str, ""),                 # JSON map {kid: secret}
    SPORTS_ODDS_JWT_ACTIVE_KID=(str, "v1"),
    SPORTS_ODDS_JWT_AUD=(str, "sports-odds-api"),
    SPORTS_ODDS_JWT_ISS=(str, "playbook-api"),
    SPORTS_ODDS_JWT_ALG=(str, "HS256"),
    SPORTS_ODDS_JWT_TTL_SECONDS=(int, 60),
    # LLM
    LLM_PROVIDER=(str, "deepseek"),
    LLM_BASE_URL=(str, "https://api.deepseek.com/v1"),
    LLM_API_KEY=(str, ""),
    LLM_MODEL=(str, "deepseek-chat"),
    LLM_TIMEOUT_SECONDS=(int, 20),
    # Push (FCM)
    FCM_PROJECT_ID=(str, ""),
    FCM_SERVICE_ACCOUNT_PATH=(str, ""),
    # Email
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_USE_SSL=(bool, False),
    DEFAULT_FROM_EMAIL=(str, "noreply@playbook.local"),
    ACCOUNT_VERIFY_EMAIL_REQUIRED=(bool, False),
)

env_file = BASE_DIR / ".env"
if env_file.is_file():
    env.read_env(str(env_file))
