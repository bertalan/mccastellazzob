"""
Context processors for the website app.

mccastellazzob.com - Moto Club Castellazzo Bormida
Context processors per aggiungere variabili globali ai template.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.translation import get_language


if TYPE_CHECKING:
    from django.http import HttpRequest


def current_language(request: HttpRequest) -> dict[str, str]:
    """
    Aggiunge la lingua corrente al contesto dei template.

    Returns:
        Dict con 'current_language' contenente il codice lingua (it, en, fr).
    """
    language_code = get_language() or "it"

    return {
        "current_language": language_code,
    }
