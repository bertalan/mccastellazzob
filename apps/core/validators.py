"""
Validatori custom.

mccastellazzob.com - Moto Club Castellazzo Bormida
Validatori riutilizzabili per form e modelli.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_coordinates(value: str) -> None:
    """
    Valida che una stringa contenga coordinate GPS valide.

    Args:
        value: Stringa nel formato "latitudine,longitudine"

    Raises:
        ValidationError: Se il formato non è valido o i valori sono fuori range.
    """
    if not value:
        return

    pattern = r"^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$"
    if not re.match(pattern, value):
        raise ValidationError(
            _("Formato coordinate non valido. Usa: latitudine,longitudine"),
            code="invalid_format",
        )

    try:
        parts = value.split(",")
        lat = float(parts[0].strip())
        lng = float(parts[1].strip())

        if not -90 <= lat <= 90:
            raise ValidationError(
                _("Latitudine deve essere tra -90 e 90 gradi."),
                code="invalid_latitude",
            )

        if not -180 <= lng <= 180:
            raise ValidationError(
                _("Longitudine deve essere tra -180 e 180 gradi."),
                code="invalid_longitude",
            )

    except (ValueError, IndexError) as exc:
        raise ValidationError(
            _("Impossibile parsare le coordinate."),
            code="parse_error",
        ) from exc


def validate_search_query(query: str | None, max_length: int = 200) -> str:
    """
    Valida e sanitizza una query di ricerca.

    Args:
        query: Query di ricerca grezza dall'utente.
        max_length: Lunghezza massima consentita.

    Returns:
        Query sanitizzata e troncata.

    Raises:
        ValidationError: Se la query contiene pattern sospetti.
    """
    if not query:
        return ""

    # Rimuovi spazi extra
    cleaned = " ".join(query.split())

    # Tronca alla lunghezza massima
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    # Pattern potenzialmente pericolosi (ReDoS prevention)
    dangerous_patterns = [
        r"(.)\1{10,}",  # Carattere ripetuto 10+ volte
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned):
            raise ValidationError(
                _("Query di ricerca non valida."),
                code="suspicious_pattern",
            )

    return cleaned
