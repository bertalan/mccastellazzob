"""
Tests for schema.org generator.

mccastellazzob.com - Moto Club Castellazzo Bormida
"""

import json
from datetime import datetime

import pytest

from apps.core.schema import SchemaOrgEvent
from apps.core.schema import SchemaOrgGenerator
from apps.core.schema import SchemaOrgPlace


class TestSchemaOrgGenerator:
    """Test per SchemaOrgGenerator."""

    def test_generate_event_basic(self):
        """Test generazione JSON-LD evento base."""
        generator = SchemaOrgGenerator()
        event = SchemaOrgEvent(
            name="Raduno Moto",
            start_date=datetime(2026, 6, 15, 10, 0),
            location_name="Castellazzo Bormida",
            address="Via Roma 1, Castellazzo Bormida AL",
            url="https://mccastellazzob.com/eventi/raduno",
        )

        result = generator.generate_event(event)
        data = json.loads(result)

        assert data["@context"] == "https://schema.org"
        assert data["@type"] == "Event"
        assert data["name"] == "Raduno Moto"
        assert "2026-06-15" in data["startDate"]
        assert data["location"]["name"] == "Castellazzo Bormida"

    def test_generate_event_with_coordinates(self):
        """Test generazione evento con coordinate GPS."""
        generator = SchemaOrgGenerator()
        event = SchemaOrgEvent(
            name="Raduno",
            start_date=datetime(2026, 6, 15),
            location_name="Piazza",
            address="Via Roma 1",
            url="https://example.com",
            latitude=44.8566,
            longitude=8.6144,
        )

        result = generator.generate_event(event)
        data = json.loads(result)

        assert "geo" in data["location"]
        assert data["location"]["geo"]["latitude"] == 44.8566
        assert data["location"]["geo"]["longitude"] == 8.6144

    def test_generate_place_basic(self):
        """Test generazione JSON-LD luogo base."""
        generator = SchemaOrgGenerator()
        place = SchemaOrgPlace(
            name="Sede Moto Club",
            address="Via Roma 1, Castellazzo Bormida",
            url="https://mccastellazzob.com/luoghi/sede",
        )

        result = generator.generate_place(place)
        data = json.loads(result)

        assert data["@context"] == "https://schema.org"
        assert data["@type"] == "Place"
        assert data["name"] == "Sede Moto Club"

    def test_generate_organization(self):
        """Test generazione JSON-LD organizzazione."""
        generator = SchemaOrgGenerator()

        result = generator.generate_organization()
        data = json.loads(result)

        assert data["@context"] == "https://schema.org"
        assert data["@type"] == "Organization"
        assert data["name"] == "Moto Club Castellazzo Bormida"
        assert data["url"] == "https://mccastellazzob.com"
