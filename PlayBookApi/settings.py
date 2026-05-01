"""Django settings for PlayBookApi.

Mirrors the TeeShotApi pattern:
- DEFAULT_APPS / PACKAGES_APPS / LOCAL_APPS split.
- Modular config aggregated via `from PlayBookApi.config import *` at the bottom.
- All env access through `env(...)` from environment.py.
"""

import json as _json
from pathlib import Path

import dj_database_url

from PlayBookApi.environment import env

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_APPS = (
    "daphne",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
)

PACKAGES_APPS = (
    "channels",
    "rest_framework",
    "rest_framework_api_key",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_celery_results",
    "django_celery_beat",
    "corsheaders",
    "import_export",
    "django_icons",
    "phonenumber_field",
    "django_rest_passwordreset",
)

LOCAL_APPS = (
    "accounts",
    "markets",
    "predictions",
    "follows",
    "notifications",
    "compliance",
)

INSTALLED_APPS = DEFAULT_APPS + PACKAGES_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "compliance.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "PlayBookApi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "PlayBookApi.wsgi.application"
ASGI_APPLICATION = "PlayBookApi.asgi.application"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOG_LEVEL = env("LOG_LEVEL")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# ── Email ──
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_USE_SSL = env("EMAIL_USE_SSL")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
ACCOUNT_VERIFY_EMAIL_REQUIRED = env("ACCOUNT_VERIFY_EMAIL_REQUIRED")

# ── S2S JWT for sports-odds-api ──
SPORTS_ODDS_API_URL = env("SPORTS_ODDS_API_URL")
_sports_odds_keys_raw = env("SPORTS_ODDS_JWT_KEYS")
try:
    SPORTS_ODDS_JWT_KEYS = _json.loads(_sports_odds_keys_raw) if _sports_odds_keys_raw else {}
except Exception:
    SPORTS_ODDS_JWT_KEYS = {}
SPORTS_ODDS_JWT_ACTIVE_KID = env("SPORTS_ODDS_JWT_ACTIVE_KID")
SPORTS_ODDS_JWT_AUD = env("SPORTS_ODDS_JWT_AUD")
SPORTS_ODDS_JWT_ISS = env("SPORTS_ODDS_JWT_ISS")
SPORTS_ODDS_JWT_ALG = env("SPORTS_ODDS_JWT_ALG")
SPORTS_ODDS_JWT_TTL_SECONDS = env("SPORTS_ODDS_JWT_TTL_SECONDS")

# ── LLM ──
LLM_PROVIDER = env("LLM_PROVIDER")
LLM_BASE_URL = env("LLM_BASE_URL")
LLM_API_KEY = env("LLM_API_KEY")
LLM_MODEL = env("LLM_MODEL")
LLM_TIMEOUT_SECONDS = env("LLM_TIMEOUT_SECONDS")

# ── Push (FCM) ──
FCM_PROJECT_ID = env("FCM_PROJECT_ID")
FCM_SERVICE_ACCOUNT_PATH = env("FCM_SERVICE_ACCOUNT_PATH")

# Modular configuration aggregated last so any `*_SETTINGS` defined here can be
# referenced by config modules via `getattr(settings, ...)` if needed.
from PlayBookApi.config import *  # noqa: E402, F401, F403
