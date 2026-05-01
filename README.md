# PlayBookApi

Sports prediction tips engine. Consumes [`sports-odds-api`](../../sports-odds-api/) and produces picks (recommended bet + bookmaker + price + confidence + LLM-generated reasoning) for upcoming matches across 12 major football leagues + US sports.

**Not a bookmaker.** No money handling, no wallets, no settlement of real bets. Just tips with explanations.

## Stack

- Django 6 + DRF + Channels (HTTP + WebSocket via daphne)
- Postgres 16 + Redis 7
- Celery + Beat (DatabaseScheduler — schedules editable via admin)
- simplejwt + google-auth + rest_framework_api_key (Cuba-friendly auth, no Firebase SDK)
- drf-spectacular (Swagger/Redoc)
- Unfold admin
- LLM provider swappable (DeepSeek default, OpenAI / Anthropic / local Ollama all supported via OpenAI-compatible API)

## Quick start (Docker)

```bash
cp .env.example .env
# Fill LLM_API_KEY, FCM_SERVICE_ACCOUNT_PATH, SPORTS_ODDS_JWT_KEYS (must match sports-odds-api map)

docker compose up -d --build
```

`sports-odds-api` must be running first (PlayBookApi joins its Docker network as external). API exposed at `http://localhost:18002`.

## Endpoints (high-level)

```
/admin/                               Unfold admin
/api/docs/                            Swagger
/api/redoc/                           Redoc
/health/live/    /health/ready/       Probes

/api/v1/auth/token/                   Login (password / google / apple)
/api/v1/auth/token/refresh/
/api/v1/auth/account/create/
/api/v1/auth/account/me/

/api/v1/markets/sports/
/api/v1/markets/matches/
/api/v1/markets/matches/<id>/odds/

/api/v1/predictions/                  List picks (filters: sport, league, status, strategy)
/api/v1/predictions/<id>/
/api/v1/strategies/
/api/v1/accuracy/?strategy=<id>

/api/v1/me/follows/sports/
/api/v1/me/saved-predictions/
/api/v1/devices/register/

ws://.../ws/matches/?sport=football    Realtime score push (proxy SSE → WS)
```

All `/api/v1/...` endpoints require:
- `Authorization: Bearer <jwt>` (user JWT from login)
- `X-Api-Key: <client_api_key>` (Flutter app key)

## Architecture

```
Flutter ──REST + WS──▶ PlayBookApi ──HTTP + JWT internal──▶ sports-odds-api ──▶ scrapers
                            │
                            └──▶ DeepSeek/OpenAI (LLM reasoning)
                            └──▶ FCM HTTP v1 (push notifications)
```

See `/Users/quasar/.claude/plans/enchanted-tickling-sparkle.md` for the full implementation plan.
