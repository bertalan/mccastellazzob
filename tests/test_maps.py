"""
MC Castellazzo - Map Utilities Tests
"""
import pytest
from unittest.mock import patch, Mock

from apps.core.maps import geocode_address, get_default_location, generate_leaflet_map_html


class TestGeocodeAddress:
    """Tests for geocode_address function."""
    
    @patch("apps.core.maps.requests.get")
    def test_geocode_success(self, mock_get):
        """Test successful geocoding."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "45.0703",
                "lon": "7.6869",
                "display_name": "Torino, Piedmont, Italy",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = geocode_address("Torino, Italy")
        
        assert result is not None
        assert result["lat"] == 45.0703
        assert result["lon"] == 7.6869
        assert "Torino" in result["display_name"]
    
    @patch("apps.core.maps.requests.get")
    def test_geocode_not_found(self, mock_get):
        """Test geocoding with no results."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = geocode_address("NonExistentPlace12345")
        
        assert result is None
    
    @patch("apps.core.maps.requests.get")
    def test_geocode_error(self, mock_get):
        """Test geocoding with network error."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = geocode_address("Torino, Italy")
        
        assert result is None


class TestGetDefaultLocation:
    """Tests for get_default_location function."""
    
    def test_default_location(self):
        """Test default location returns Torino."""
        location = get_default_location()
        
        assert location["city"] == "Torino"
        assert location["region"] == "Piedmont"
        assert location["country"] == "IT"
        assert "lat" in location
        assert "lon" in location


class TestGenerateLeafletMapHtml:
    """Tests for generate_leaflet_map_html function."""
    
    def test_basic_map(self):
        """Test basic map HTML generation."""
        html = generate_leaflet_map_html(lat=45.0703, lon=7.6869)
        
        assert 'id="map"' in html
        assert "45.0703" in html
        assert "7.6869" in html
        assert "leaflet.js" in html
        assert "openstreetmap.org" in html
    
    def test_map_with_marker_text(self):
        """Test map with marker popup."""
        html = generate_leaflet_map_html(
            lat=45.0703,
            lon=7.6869,
            marker_text="MC Castellazzo",
        )
        
        assert "MC Castellazzo" in html
        assert "bindPopup" in html
    
    def test_custom_map_id(self):
        """Test map with custom ID."""
        html = generate_leaflet_map_html(
            lat=45.0703,
            lon=7.6869,
            map_id="custom-map",
        )
        
        assert 'id="custom-map"' in html
    
    def test_custom_height(self):
        """Test map with custom height."""
        html = generate_leaflet_map_html(
            lat=45.0703,
            lon=7.6869,
            height="600px",
        )
        
        assert "height: 600px" in html
