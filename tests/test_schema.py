"""
MC Castellazzo - Schema.org Tests
"""
import pytest
import json

from apps.core.schema import (
    SchemaOrgMixin,
    postal_address,
    contact_point,
    image_object,
    place,
    article,
    event,
    person,
)


class TestPostalAddress:
    """Tests for postal_address function."""
    
    def test_basic_address(self):
        """Test basic address generation with minimal params."""
        addr = postal_address()
        
        assert addr["@type"] == "PostalAddress"
        # Default country is IT, other fields are empty
        assert addr["addressCountry"] == "IT"
        assert "addressLocality" not in addr  # No default city
        assert "addressRegion" not in addr     # No default region
    
    def test_full_address(self):
        """Test address with all fields."""
        addr = postal_address(
            street="Via Roma 1",
            city="Milano",
            region="Lombardy",
            country="IT",
            postal_code="20100",
        )
        
        assert addr["streetAddress"] == "Via Roma 1"
        assert addr["addressLocality"] == "Milano"
        assert addr["postalCode"] == "20100"


class TestContactPoint:
    """Tests for contact_point function."""
    
    def test_basic_contact(self):
        """Test basic contact point."""
        contact = contact_point(
            telephone="+39 011 1234567",
            email="info@example.com",
        )
        
        assert contact["@type"] == "ContactPoint"
        assert contact["telephone"] == "+39 011 1234567"
        assert contact["email"] == "info@example.com"
        assert contact["contactType"] == "customer service"


class TestImageObject:
    """Tests for image_object function."""
    
    def test_basic_image(self):
        """Test basic image object."""
        img = image_object(url="https://example.com/image.jpg")
        
        assert img["@type"] == "ImageObject"
        assert img["url"] == "https://example.com/image.jpg"
    
    def test_image_with_dimensions(self):
        """Test image object with dimensions."""
        img = image_object(
            url="https://example.com/image.jpg",
            width=800,
            height=600,
            caption="Test image",
        )
        
        assert img["width"] == 800
        assert img["height"] == 600
        assert img["caption"] == "Test image"


class TestPlace:
    """Tests for place function."""
    
    def test_basic_place(self):
        """Test basic place with only name."""
        p = place(name="Piazza Castello")
        
        assert p["@type"] == "Place"
        assert p["name"] == "Piazza Castello"
        # Address is only included if street/city/region are provided
        assert "address" not in p
    
    def test_place_with_address(self):
        """Test place with address."""
        p = place(name="Piazza Castello", city="Torino", region="Piemonte")
        
        assert p["@type"] == "Place"
        assert "address" in p
        assert p["address"]["addressLocality"] == "Torino"
    
    def test_place_with_geo(self):
        """Test place with coordinates."""
        p = place(
            name="Piazza Castello",
            lat=45.0715,
            lon=7.6858,
        )
        
        assert "geo" in p
        assert p["geo"]["@type"] == "GeoCoordinates"
        assert p["geo"]["latitude"] == 45.0715
        assert p["geo"]["longitude"] == 7.6858


class TestArticle:
    """Tests for article function."""
    
    def test_basic_article(self):
        """Test basic article."""
        art = article(headline="Test Article")
        
        assert art["@type"] == "Article"
        assert art["headline"] == "Test Article"
    
    def test_full_article(self):
        """Test article with all fields."""
        art = article(
            headline="Test Article",
            image_url="https://example.com/image.jpg",
            date_published="2025-01-11",
            article_section="News",
            url="https://example.com/article",
            description="Article description",
        )
        
        assert art["image"] == "https://example.com/image.jpg"
        assert art["datePublished"] == "2025-01-11"
        assert art["articleSection"] == "News"


class TestEvent:
    """Tests for event function."""
    
    def test_basic_event(self):
        """Test basic event."""
        evt = event(
            name="Raduno Moto",
            start_date="2025-06-15T10:00:00",
        )
        
        assert evt["@type"] == "Event"
        assert evt["name"] == "Raduno Moto"
        assert evt["startDate"] == "2025-06-15T10:00:00"
        assert "EventScheduled" in evt["eventStatus"]
    
    def test_cancelled_event(self):
        """Test cancelled event."""
        evt = event(
            name="Raduno Moto",
            start_date="2025-06-15T10:00:00",
            event_status="EventCancelled",
        )
        
        assert "EventCancelled" in evt["eventStatus"]


class TestPerson:
    """Tests for person function."""
    
    def test_basic_person(self):
        """Test basic person."""
        p = person(name="Mario Rossi")
        
        assert p["@type"] == "Person"
        assert p["name"] == "Mario Rossi"
    
    def test_person_with_role(self):
        """Test person with job title."""
        p = person(
            name="Mario Rossi",
            job_title="Presidente",
            image_url="https://example.com/photo.jpg",
        )
        
        assert p["jobTitle"] == "Presidente"
        assert p["image"] == "https://example.com/photo.jpg"
