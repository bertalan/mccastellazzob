"""
Tests for context processors.

mccastellazzob.com - Moto Club Castellazzo Bormida
"""

import pytest
from django.test import RequestFactory
from django.utils import translation

from apps.website.context_processors import current_language


@pytest.mark.django_db
class TestCurrentLanguageContextProcessor:
    """Test per current_language context processor."""

    def test_returns_italian_default(self):
        """Test che restituisca italiano come default."""
        factory = RequestFactory()
        request = factory.get("/")

        with translation.override("it"):
            result = current_language(request)

        assert "current_language" in result
        assert result["current_language"] == "it"

    def test_returns_english(self):
        """Test che restituisca inglese."""
        factory = RequestFactory()
        request = factory.get("/en/")

        with translation.override("en"):
            result = current_language(request)

        assert result["current_language"] == "en"

    def test_returns_french(self):
        """Test che restituisca francese."""
        factory = RequestFactory()
        request = factory.get("/fr/")

        with translation.override("fr"):
            result = current_language(request)

        assert result["current_language"] == "fr"
