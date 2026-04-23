"""Development settings — used during local development.

Usage:
    DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development python manage.py runserver
    (or set in .env / manage.py)
"""

from .base import *  # noqa: F401,F403

# --------------------------------------------------
# SECURITY (relaxed for local dev)
# --------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-zg73ur7um80hpb!@-&o#ii+moa$y9zg)i!g($lq+8oh=dyjw&t",
)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# --------------------------------------------------
# DATABASE — Neon PostgreSQL (cloud)
# Using IP directly because corporate DNS blocks external queries.
# The endpoint option tells Neon's pooler which project to route to.
# --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "52.220.170.93",        # Resolved IP of Neon pooler
        "PORT": "5432",
        "NAME": "neondb",
        "USER": "neondb_owner",
        "PASSWORD": "npg_7EzFce1jbGTM",
        "OPTIONS": {
            "sslmode": "require",
            "options": "endpoint=ep-winter-hall-a1y923vf-pooler",
        },
        "CONN_MAX_AGE": 600,
    }
}

# --------------------------------------------------
# LOGGING (verbose in dev)
# --------------------------------------------------
LOGGING["loggers"]["generator"]["level"] = "DEBUG"  # type: ignore[index]

# Print emails to terminal during local development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

