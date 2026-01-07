"""
Django base settings for mccastellazzob project.

mccastellazzob.com - Moto Club Castellazzo Bormida
Stack: CodeRedCMS 6.0 / Wagtail 7.0 LTS / Django 5.2 LTS
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS: list[str] = []


# ==============================================
# APPLICATION DEFINITION
# ==============================================

INSTALLED_APPS = [
    # Project apps
    "apps.website",
    "apps.media",
    "apps.users",
    # Wagtail CRX (CodeRed Extensions)
    "coderedcms",
    "django_bootstrap5",
    "modelcluster",
    "taggit",
    "wagtailcache",
    "wagtailseo",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.admin",
    # Internationalization
    "wagtail.locales",
    "wagtail.contrib.simple_translation",
    # OpenStreetMap
    "wagtailgeowidget",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    # Cache - must be FIRST
    "wagtailcache.cache.UpdateCacheMiddleware",
    # Common functionality
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Security
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # CMS functionality
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    # Cache - must be LAST
    "wagtailcache.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "mccastellazzob.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "apps.website.context_processors.current_language",
            ],
        },
    },
]

WSGI_APPLICATION = "mccastellazzob.wsgi.application"


# ==============================================
# DATABASE
# ==============================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "mccastellazzob"),
        "USER": os.environ.get("DB_USER", "mccastellazzob"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


# ==============================================
# PASSWORD VALIDATION
# ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "users.User"


# ==============================================
# INTERNATIONALIZATION
# ==============================================

LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Wagtail i18n
WAGTAIL_I18N_ENABLED = True
WAGTAILSIMPLETRANSLATION_SYNC_PAGE_TREE = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("it", "Italiano"),
    ("en", "English"),
    ("fr", "Français"),
]

WAGTAILADMIN_PERMITTED_LANGUAGES = [
    ("it", "Italiano"),
    ("en", "English"),
    ("fr", "Français"),
]


# ==============================================
# STATIC FILES
# ==============================================

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


# ==============================================
# LOGIN
# ==============================================

LOGIN_URL = "wagtailadmin_login"
LOGIN_REDIRECT_URL = "wagtailadmin_home"


# ==============================================
# WAGTAIL SETTINGS
# ==============================================

WAGTAIL_SITE_NAME = "Moto Club Castellazzo Bormida"
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILIMAGES_IMAGE_MODEL = "media.CustomImage"
WAGTAILDOCS_DOCUMENT_MODEL = "media.CustomDocument"
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "https://mccastellazzob.com")

# Disable built-in CRX Navbar and Footer (using custom implementation)
CRX_DISABLE_NAVBAR = True
CRX_DISABLE_FOOTER = True


# ==============================================
# TAGS
# ==============================================

TAGGIT_CASE_INSENSITIVE = True


# ==============================================
# OTHER SETTINGS
# ==============================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
