"""
MC Castellazzo - Safe HTTP Client
==================================
Wrapper su `requests` con allowlist di host esterni (mitigazione SSRF, V2-018).

Uso:
    from apps.core.http_safe import safe_get
    response = safe_get("https://nominatim.openstreetmap.org/search", params={...})

L'allowlist è definita in settings.ALLOWED_OUTBOUND_HOSTS. Se l'host non è
nell'allowlist viene sollevato `OutboundHostNotAllowed` (sottoclasse di
`requests.RequestException` per essere catturata dai gestori esistenti).
"""
from __future__ import annotations

import logging
from urllib.parse import urlparse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Default allowlist — i servizi esterni effettivamente usati dal sito.
# Override in settings.ALLOWED_OUTBOUND_HOSTS (set/list di hostname).
DEFAULT_ALLOWED_OUTBOUND_HOSTS: frozenset[str] = frozenset({
    "nominatim.openstreetmap.org",
    "translate.googleapis.com",
    "translate.google.com",
    # I tile OSM e gli script CDN sono caricati lato browser, non server-side.
})


class OutboundHostNotAllowed(requests.RequestException):
    """Sollevata quando un URL punta a un host non in allowlist."""


def _allowed_hosts() -> frozenset[str]:
    configured = getattr(settings, "ALLOWED_OUTBOUND_HOSTS", None)
    if configured is None:
        return DEFAULT_ALLOWED_OUTBOUND_HOSTS
    return frozenset(configured)


def _validate_url(url: str) -> None:
    """Valida schema + host. Solleva `OutboundHostNotAllowed` se non consentito."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise OutboundHostNotAllowed(
            f"Schema non consentito: {parsed.scheme!r} (atteso http/https)"
        )
    host = (parsed.hostname or "").lower()
    if not host:
        raise OutboundHostNotAllowed("URL senza host")
    allowed = _allowed_hosts()
    if host not in allowed:
        logger.warning("Blocked outbound request to non-allowlisted host: %s", host)
        raise OutboundHostNotAllowed(f"Host non in allowlist: {host}")


def safe_request(method: str, url: str, **kwargs) -> requests.Response:
    """Esegue una richiesta HTTP solo verso host in allowlist."""
    _validate_url(url)
    # Default timeout difensivo se il chiamante non lo passa
    kwargs.setdefault("timeout", 10)
    # Disabilita redirect cross-host: i redirect possono sfuggire all'allowlist
    kwargs.setdefault("allow_redirects", False)
    return requests.request(method, url, **kwargs)


def safe_get(url: str, **kwargs) -> requests.Response:
    return safe_request("GET", url, **kwargs)


def safe_post(url: str, **kwargs) -> requests.Response:
    return safe_request("POST", url, **kwargs)
