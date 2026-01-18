"""
MC Castellazzo - Django Settings Base
=====================================
Configurazione base per CodeRedCMS/Wagtail con supporto 4 lingue.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-production")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.table_block",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # Wagtail Localize
    "wagtail_localize",
    "wagtail_localize.locales",
    # CodeRedCMS
    "coderedcms",
    "wagtailseo",
    "wagtailcache",
    "django_bootstrap5",
    "modelcluster",
    "taggit",
    # Allauth (frontend auth)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Jinja2
    "django_jinja",
    # Our apps
    "apps.core",
    "apps.website",
    "apps.custom_user",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Wagtail
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    # Allauth
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "mccastellazzob.urls"

# Templates configuration with Jinja2 + Django
TEMPLATES = [
    # Jinja2 for frontend templates
    {
        "BACKEND": "django_jinja.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "match_extension": ".jinja2",
            "match_regex": r"^(?!admin/).*",
            "app_dirname": "jinja2",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "wagtail.contrib.settings.context_processors.settings",
                "apps.core.context_processors.schema_org",
                "apps.core.context_processors.site_colors",
                "apps.core.context_processors.navigation",
                "apps.core.context_processors.main_pages",
                "apps.core.context_processors.page_translations",
            ],
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.DebugExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "wagtail.jinja2tags.core",
                "wagtail.images.jinja2tags.images",
            ],
            "globals": {
                "now": "django.utils.timezone.now",
                "localtime": "django.utils.timezone.localtime",
            },
            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",
        },
    },
    # Django templates for admin and Wagtail
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "mccastellazzob.wsgi.application"

# Database (override in specific settings)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": False,
    }
}

# Auth
AUTH_USER_MODEL = "custom_user.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ======================
# INTERNATIONALIZATION
# 4 lingue paritarie
# ======================
LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Lingue supportate (paritarie) - 5 lingue
LANGUAGES = [
    ("it", "Italiano"),
    ("en", "English"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("es", "Español"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Wagtail Localize
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES

# ======================
# STATIC FILES
# ======================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================
# WAGTAIL SETTINGS
# ======================
WAGTAIL_SITE_NAME = "MC Castellazzo"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# ======================
# WAGTAIL LOCALIZE - TRADUZIONE AUTOMATICA
# ======================
# Usa deep-translator (Google Translate gratuito) per traduzioni con un clic
WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "apps.core.machine_translator.DeepTranslatorMachineTranslator",
    "OPTIONS": {
        # Ritardo tra le richieste per evitare rate limiting (in secondi)
        "DELAY": 0.5,
    },
}

# CodeRedCMS
CODERED_PROTECTED_MEDIA_URL = "/protected/"
CODERED_PROTECTED_MEDIA_ROOT = BASE_DIR / "protected"
CODERED_PROTECTED_MEDIA_UPLOAD_WHITELIST = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]

# Disabilita Navbar e Footer built-in di CodeRedCMS per usare quelli custom multilingua
# I nostri snippet in apps.website.models.snippets usano TranslatableMixin per supporto 5 lingue
CRX_DISABLE_NAVBAR = True
CRX_DISABLE_FOOTER = True

# ======================
# ALLAUTH SETTINGS (aggiornato per allauth 65+)
# ======================
SITE_ID = 1
# Nuova configurazione allauth 65+
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ======================
# COLORI TEMA
# ======================
THEME_COLORS = {
    "oro": "#D4AF37",
    "blu_nautico": "#1B263B",
    "amaranto": "#9B1D64",
}

# ======================
# OPENSTREETMAP / NOMINATIM
# ======================
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
NOMINATIM_USER_AGENT = "MCCastellazzo/1.0"
DEFAULT_LOCATION = {
    "lat": 45.0703,
    "lon": 7.6869,
    "city": "Torino",
    "region": "Piedmont",
    "country": "IT",
}
