"""
MC Castellazzo - Test Settings
"""
from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# Use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Email to memory
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable whitenoise
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Disable debug toolbar
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]  # noqa: F405
