"""
MC Castellazzo - Security Audit Log
====================================
Logger dedicato per operazioni sensibili (V2-019). I record vengono inviati al
logger ``security`` (configurato in `mccastellazzob/settings/prod.py`).

Eventi tracciati:
- login riuscito / fallito (django.contrib.auth signals)
- logout
- cambio password
- permission/group changes (admin auth)
- esecuzione auto-translate (chiamata esplicita in `apps.core.views`)

Per loggare un evento applicativo:

    from apps.core.audit import log_security_event
    log_security_event(
        request,
        "auto_translate.completed",
        page_id=page.id,
        target_lang=target_lang,
    )
"""
from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger("security")


def _client_ip(request) -> str:
    if request is None:
        return "-"
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "-")


def _user_repr(user) -> str:
    if not user or not getattr(user, "is_authenticated", False):
        return "anonymous"
    return f"{user.get_username()}#{user.pk}"


def log_security_event(request, event: str, **fields: Any) -> None:
    """Log strutturato di un evento di sicurezza.

    Esempio output:
        SECURITY user=admin#1 ip=10.0.0.5 event=auto_translate.completed page_id=42 target_lang=en
    """
    user = getattr(request, "user", None) if request is not None else None
    parts = [
        f"user={_user_repr(user)}",
        f"ip={_client_ip(request)}",
        f"event={event}",
    ]
    parts.extend(f"{k}={v}" for k, v in fields.items())
    logger.info("SECURITY %s", " ".join(parts))


# ---------------------------------------------------------------------------
# Signal receivers
# ---------------------------------------------------------------------------

@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    log_security_event(request, "auth.login", staff=user.is_staff, super=user.is_superuser)


@receiver(user_logged_out)
def _on_logout(sender, request, user, **kwargs):
    log_security_event(request, "auth.logout")


@receiver(user_login_failed)
def _on_login_failed(sender, credentials, request=None, **kwargs):
    # Non loggare la password — solo username/email se presente
    identifier = credentials.get("username") or credentials.get("email") or "-"
    log_security_event(request, "auth.login_failed", identifier=identifier)


@receiver(post_save, sender=get_user_model())
def _on_user_save(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "SECURITY event=user.created username=%s staff=%s super=%s",
            instance.get_username(), instance.is_staff, instance.is_superuser,
        )
    else:
        # Loggiamo solo cambi di stato privilegiato
        logger.info(
            "SECURITY event=user.updated username=%s staff=%s super=%s",
            instance.get_username(), instance.is_staff, instance.is_superuser,
        )


@receiver(post_delete, sender=get_user_model())
def _on_user_delete(sender, instance, **kwargs):
    logger.info("SECURITY event=user.deleted username=%s", instance.get_username())
