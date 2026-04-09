"""Production settings — used in deployed environments.

Usage:
    DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production gunicorn ai_formal_generator.wsgi
    (or set in .env)

All secrets MUST come from environment variables.
"""


from .base import *  # noqa: F401,F403

# --------------------------------------------------
# SECURITY (strict)
# --------------------------------------------------
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # MUST be set — crash on missing

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Use database-backed sessions (document data can be large)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# --------------------------------------------------
# DATABASE (use env var; falls back to SQLite for simple deploys)
# --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
        "CONN_MAX_AGE": 600,  # reuse DB connections for 10 minutes
        "CONN_HEALTH_CHECKS": True,  # verify connections before reuse (Django 4.1+)
    }
}

# --------------------------------------------------
# STATIC FILES (collected for serving via nginx / whitenoise)
# --------------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------
# LOGGING (structured, file-based in production)
# --------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING["handlers"]["file"] = {  # type: ignore[index]
    "class": "logging.handlers.RotatingFileHandler",
    "filename": str(LOG_DIR / "app.log"),
    "maxBytes": 10 * 1024 * 1024,  # 10 MB
    "backupCount": 5,
    "formatter": "verbose",
}
LOGGING["root"]["handlers"] = ["console", "file"]  # type: ignore[index]
LOGGING["loggers"]["generator"]["handlers"] = ["console", "file"]  # type: ignore[index]
LOGGING["loggers"]["generator"]["level"] = "INFO"  # type: ignore[index]
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]  # type: ignore[index]

