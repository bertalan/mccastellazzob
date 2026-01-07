"""
Docker settings for mccastellazzob.com.

Solo per sviluppo locale! In produzione NON si usa Docker.
"""

from __future__ import annotations

import os

from .base import *  # noqa: F401, F403


DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-changeme-in-production"
)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Database PostgreSQL via variabili d'ambiente
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "mccastellazzob"),
        "USER": os.environ.get("POSTGRES_USER", "mccastellazzob"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Static e media
STATIC_URL = "/static/"
STATIC_ROOT = "/app/static"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

# Cache in memoria per Docker dev
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email - console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Wagtail
WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL", "http://localhost:8000"
)
