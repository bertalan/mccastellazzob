"""
MC Castellazzo - Core App Config
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Registra i receiver del security audit log (V2-019)
        from apps.core import audit  # noqa: F401
