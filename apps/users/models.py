"""
Custom user model.

mccastellazzob.com - Moto Club Castellazzo Bormida
Modello utente con email come identificatore principale.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


if TYPE_CHECKING:
    from typing import Any


class UserManager(BaseUserManager["User"]):
    """
    Manager custom per User con email come identificatore.

    Gestisce la creazione di utenti normali e superuser
    usando l'email invece dello username.
    """

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Crea e salva un utente con email e password.

        Args:
            email: Email dell'utente (obbligatoria).
            password: Password dell'utente.
            **extra_fields: Campi aggiuntivi.

        Returns:
            Istanza User creata.

        Raises:
            ValueError: Se email non fornita.
        """
        if not email:
            raise ValueError(_("L'email è obbligatoria"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Crea e salva un superuser con email e password.

        Args:
            email: Email del superuser.
            password: Password del superuser.
            **extra_fields: Campi aggiuntivi.

        Returns:
            Istanza User superuser creata.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser deve avere is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser deve avere is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modello utente custom con email come identificatore.

    Usa l'email invece dello username per l'autenticazione.
    Lo username viene comunque mantenuto per compatibilità Wagtail.
    """

    email = models.EmailField(
        verbose_name=_("Email"),
        unique=True,
        help_text=_("Indirizzo email per login e comunicazioni."),
    )

    # Username opzionale (per compatibilità)
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=150,
        blank=True,
        help_text=_("Username opzionale."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = _("Utente")
        verbose_name_plural = _("Utenti")

    def __str__(self) -> str:
        return self.email
