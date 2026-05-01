SPECTACULAR_SETTINGS = {
    "TITLE": "PlayBookApi",
    "DESCRIPTION": "Sports prediction tips engine. Recommended bets with LLM-explained reasoning.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayRequestDuration": True,
        "persistAuthorization": True,
    },
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "User JWT (from /api/v1/auth/token/).",
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Api-Key",
                "description": "Client API key (Flutter app).",
            },
        },
    },
    "SECURITY": [{"BearerAuth": [], "ApiKeyAuth": []}],
}
