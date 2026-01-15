"""
MC Castellazzo - Custom User Model
===================================
User model personalizzato per il sito.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    User model personalizzato con campi aggiuntivi.
    """
    # Lingua preferita
    preferred_language = models.CharField(
        _("Lingua preferita"),
        max_length=5,
        choices=[
            ("it", "Italiano"),
            ("fr", "Français"),
            ("es", "Español"),
            ("en", "English"),
        ],
        default="it",
    )
    
    # Telefono
    phone = models.CharField(
        _("Telefono"),
        max_length=20,
        blank=True,
    )
    
    # Membro del club
    is_member = models.BooleanField(
        _("Membro del club"),
        default=False,
    )
    
    # Data iscrizione club
    membership_date = models.DateField(
        _("Data iscrizione"),
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Utente")
        verbose_name_plural = _("Utenti")
    
    def __str__(self):
        return self.get_full_name() or self.username
