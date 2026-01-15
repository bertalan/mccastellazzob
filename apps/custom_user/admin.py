"""
MC Castellazzo - Custom User Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizzato per User."""
    
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_member",
        "preferred_language",
        "is_staff",
    )
    list_filter = BaseUserAdmin.list_filter + ("is_member", "preferred_language")
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("Informazioni Club"),
            {
                "fields": (
                    "phone",
                    "preferred_language",
                    "is_member",
                    "membership_date",
                )
            },
        ),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("Informazioni Club"),
            {
                "fields": (
                    "email",
                    "phone",
                    "preferred_language",
                )
            },
        ),
    )
