"""
App configuration for website.
"""

from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    """Configuration for the website app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"
    label = "website"
    verbose_name = "Website"
