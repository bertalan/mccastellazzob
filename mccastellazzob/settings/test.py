"""
Django test settings.

mccastellazzob.com - Moto Club Castellazzo Bormida
Settings for pytest execution.
"""

from .base import *  # noqa: F401, F403


DEBUG = False

SECRET_KEY = "test-secret-key-only-for-testing-not-for-production"

# Database - SQLite per velocità nei test
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable cache in tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

WAGTAIL_CACHE = False

# Faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Logging - minimal in tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "DEBUG",
    },
}

ALLOWED_HOSTS = ["*"]
WAGTAILADMIN_BASE_URL = "http://testserver"
