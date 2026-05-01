from django.urls import reverse_lazy

from PlayBookApi.environment import env


def environment_callback(request):
    if env("DJANGO_DEBUG"):
        return ["Development", "warning"]
    return ["Production", "success"]


def environment_title_prefix(request):
    if env("DJANGO_DEBUG"):
        return "[DEV]"
    return None


UNFOLD = {
    "SITE_TITLE": "PlayBookApi",
    "SITE_HEADER": "PlayBook",
    "SITE_SUBHEADER": "Sports tips engine",
    "SITE_URL": None,
    "THEME": "dark",
    "DASHBOARD_CALLBACK": "PlayBookApi.dashboard.dashboard_callback",
    "ENVIRONMENT": "PlayBookApi.config.unfold.environment_callback",
    "ENVIRONMENT_TITLE_PREFIX": "PlayBookApi.config.unfold.environment_title_prefix",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    # Muted indigo palette (different from sports-odds-api green so both admins are visually distinct)
    "COLORS": {
        "primary": {
            "50": "oklch(97% .01 270)",
            "100": "oklch(93% .03 270)",
            "200": "oklch(88% .06 268)",
            "300": "oklch(80% .09 266)",
            "400": "oklch(70% .12 264)",
            "500": "oklch(58% .14 262)",
            "600": "oklch(50% .13 260)",
            "700": "oklch(43% .11 260)",
            "800": "oklch(37% .09 262)",
            "900": "oklch(32% .07 264)",
            "950": "oklch(22% .05 264)",
        },
    },
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "command_search": True,
        "navigation": [
            {
                "title": "External Links",
                "separator": True,
                "items": [
                    {"title": "Swagger Docs", "icon": "api", "link": reverse_lazy("swagger-ui")},
                    {"title": "Redoc", "icon": "menu_book", "link": reverse_lazy("redoc")},
                    {"title": "Health (ready)", "icon": "monitor_heart", "link": reverse_lazy("health-readiness")},
                ],
            },
            {
                "title": "Authentication",
                "separator": True,
                "items": [
                    {"title": "Users", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "Groups", "icon": "group", "link": reverse_lazy("admin:auth_group_changelist")},
                    {"title": "API Keys", "icon": "key", "link": reverse_lazy("admin:rest_framework_api_key_apikey_changelist")},
                ],
            },
            {
                "title": "Markets",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Sports", "icon": "sports", "link": reverse_lazy("admin:markets_sport_changelist")},
                    {"title": "Leagues", "icon": "emoji_events", "link": reverse_lazy("admin:markets_league_changelist")},
                    {"title": "Teams", "icon": "groups", "link": reverse_lazy("admin:markets_team_changelist")},
                    {"title": "Events", "icon": "scoreboard", "link": reverse_lazy("admin:markets_event_changelist")},
                    {"title": "Bookmakers", "icon": "storefront", "link": reverse_lazy("admin:markets_bookmaker_changelist")},
                    {"title": "Odds", "icon": "trending_up", "link": reverse_lazy("admin:markets_oddssnapshot_changelist")},
                ],
            },
            {
                "title": "Predictions",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Strategies", "icon": "tune", "link": reverse_lazy("admin:predictions_strategy_changelist")},
                    {"title": "Predictions", "icon": "casino", "link": reverse_lazy("admin:predictions_prediction_changelist")},
                    {"title": "Feature Vectors", "icon": "bubble_chart", "link": reverse_lazy("admin:predictions_featurevector_changelist")},
                ],
            },
            {
                "title": "Engagement",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Profiles", "icon": "badge", "link": reverse_lazy("admin:accounts_profile_changelist")},
                    {"title": "Device Tokens", "icon": "devices", "link": reverse_lazy("admin:notifications_devicetoken_changelist")},
                    {"title": "Notification Log", "icon": "notifications", "link": reverse_lazy("admin:notifications_notificationlog_changelist")},
                ],
            },
            {
                "title": "Background Tasks",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Periodic Tasks", "icon": "schedule", "link": reverse_lazy("admin:django_celery_beat_periodictask_changelist")},
                    {"title": "Crontabs", "icon": "more_time", "link": reverse_lazy("admin:django_celery_beat_crontabschedule_changelist")},
                    {"title": "Intervals", "icon": "timer", "link": reverse_lazy("admin:django_celery_beat_intervalschedule_changelist")},
                    {"title": "Task Results", "icon": "task_alt", "link": reverse_lazy("admin:django_celery_results_taskresult_changelist")},
                ],
            },
            {
                "title": "Compliance",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Audit Log", "icon": "policy", "link": reverse_lazy("admin:compliance_auditlog_changelist")},
                ],
            },
        ],
    },
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
}
