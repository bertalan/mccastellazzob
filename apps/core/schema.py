"""
Generatore JSON-LD schema.org.

mccastellazzob.com - Moto Club Castellazzo Bormida
Genera markup strutturato per SEO secondo le specifiche schema.org.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SchemaOrgEvent:
    """Rappresenta un evento per schema.org/Event."""

    name: str
    start_date: datetime
    location_name: str
    address: str
    url: str
    end_date: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str = ""
    image_url: str = ""
    organizer_name: str = "Moto Club Castellazzo Bormida"


@dataclass
class SchemaOrgPlace:
    """Rappresenta una località per schema.org/Place."""

    name: str
    address: str
    url: str
    latitude: float | None = None
    longitude: float | None = None
    description: str = ""
    image_url: str = ""


class SchemaOrgGenerator:
    """
    Genera markup JSON-LD per schema.org.

    Supporta la generazione di markup strutturato per:
    - Event (eventi)
    - Place (località)
    - Organization (organizzazione)
    """

    CONTEXT = "https://schema.org"

    def generate_event(self, event: SchemaOrgEvent) -> str:
        """Genera JSON-LD per un evento."""
        data: dict[str, Any] = {
            "@context": self.CONTEXT,
            "@type": "Event",
            "name": event.name,
            "startDate": event.start_date.isoformat(),
            "url": event.url,
            "organizer": {
                "@type": "Organization",
                "name": event.organizer_name,
            },
        }

        if event.end_date:
            data["endDate"] = event.end_date.isoformat()

        if event.description:
            data["description"] = event.description

        if event.image_url:
            data["image"] = event.image_url

        location_data: dict[str, Any] = {
            "@type": "Place",
            "name": event.location_name,
            "address": event.address,
        }

        if event.latitude and event.longitude:
            location_data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": event.latitude,
                "longitude": event.longitude,
            }

        data["location"] = location_data

        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_place(self, place: SchemaOrgPlace) -> str:
        """Genera JSON-LD per una località."""
        data: dict[str, Any] = {
            "@context": self.CONTEXT,
            "@type": "Place",
            "name": place.name,
            "address": place.address,
            "url": place.url,
        }

        if place.description:
            data["description"] = place.description

        if place.image_url:
            data["image"] = place.image_url

        if place.latitude and place.longitude:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": place.latitude,
                "longitude": place.longitude,
            }

        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_organization(
        self,
        name: str = "Moto Club Castellazzo Bormida",
        url: str = "https://mccastellazzob.com",
        logo_url: str = "",
    ) -> str:
        """Genera JSON-LD per l'organizzazione."""
        data: dict[str, Any] = {
            "@context": self.CONTEXT,
            "@type": "Organization",
            "name": name,
            "url": url,
        }

        if logo_url:
            data["logo"] = logo_url

        return json.dumps(data, ensure_ascii=False, indent=2)
