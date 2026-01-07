"""
Tests for core validators.

mccastellazzob.com - Moto Club Castellazzo Bormida
"""

import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import validate_coordinates
from apps.core.validators import validate_search_query


class TestValidateCoordinates:
    """Test per validate_coordinates."""

    def test_valid_coordinates(self):
        """Test coordinate valide."""
        # Non deve sollevare eccezioni
        validate_coordinates("44.8566,8.6144")
        validate_coordinates("0,0")
        validate_coordinates("-90,-180")
        validate_coordinates("90,180")

    def test_empty_value(self):
        """Test valore vuoto (valido)."""
        validate_coordinates("")
        validate_coordinates(None)  # type: ignore

    def test_invalid_format(self):
        """Test formato non valido."""
        with pytest.raises(ValidationError):
            validate_coordinates("invalid")

        with pytest.raises(ValidationError):
            validate_coordinates("44.8566")

    def test_latitude_out_of_range(self):
        """Test latitudine fuori range."""
        with pytest.raises(ValidationError):
            validate_coordinates("91,0")

        with pytest.raises(ValidationError):
            validate_coordinates("-91,0")

    def test_longitude_out_of_range(self):
        """Test longitudine fuori range."""
        with pytest.raises(ValidationError):
            validate_coordinates("0,181")

        with pytest.raises(ValidationError):
            validate_coordinates("0,-181")


class TestValidateSearchQuery:
    """Test per validate_search_query."""

    def test_valid_query(self):
        """Test query valida."""
        result = validate_search_query("motoclub eventi")
        assert result == "motoclub eventi"

    def test_empty_query(self):
        """Test query vuota."""
        assert validate_search_query("") == ""
        assert validate_search_query(None) == ""

    def test_query_trimmed(self):
        """Test rimozione spazi extra."""
        result = validate_search_query("  motoclub   eventi  ")
        assert result == "motoclub eventi"

    def test_query_truncated(self):
        """Test troncamento query lunga."""
        long_query = "a" * 300
        result = validate_search_query(long_query, max_length=200)
        assert len(result) == 200

    def test_suspicious_pattern(self):
        """Test pattern sospetti (ReDoS)."""
        with pytest.raises(ValidationError):
            validate_search_query("aaaaaaaaaaaaaaaaaaaaaa")  # 22 'a'
