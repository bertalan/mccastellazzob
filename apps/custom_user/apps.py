"""
MC Castellazzo - Custom User App Config
"""
from django.apps import AppConfig


class CustomUserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.custom_user"
    verbose_name = "Utenti"
