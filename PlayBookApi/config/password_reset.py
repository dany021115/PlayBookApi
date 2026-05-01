"""6-digit numeric PIN tokens for password reset (dlujo pattern)."""

DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomNumberTokenGenerator",
    "OPTIONS": {
        "min_number": 111111,
        "max_number": 999999,
    },
}
