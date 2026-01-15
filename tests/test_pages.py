"""
MC Castellazzo - Page Model Tests
"""
import pytest
import uuid
from datetime import date, datetime

from wagtail.models import Page

from apps.website.models import (
    HomePage,
    TimelinePage,
    AboutPage,
    BoardPage,
    TransparencyPage,
    ContactPage,
    EventsPage,
    EventDetailPage,
    EventsArchivePage,
)


@pytest.mark.django_db
class TestHomePage:
    """Tests for HomePage model."""
    
    def test_homepage_creation(self, site):
        """Test homepage exists after site fixture."""
        home = HomePage.objects.first()
        assert home is not None
        assert home.organization_name is not None  # Nome dinamico dalla fixture
    
    def test_homepage_schema_org_type(self, site):
        """Test homepage schema.org type is Organization."""
        home = HomePage.objects.first()
        assert home.get_schema_org_type() == "Organization"
    
    def test_homepage_schema_org_data(self, site):
        """Test homepage schema.org data."""
        home = HomePage.objects.first()
        home.telephone = "+39 011 1234567"
        home.email = "info@mccastellazzob.com"
        home.founding_date = date(1975, 1, 1)
        home.save()
        
        data = home.get_schema_org_data()
        
        assert data["name"] == home.organization_name  # Nome dinamico
        assert data["knowsAbout"] == "Motoclub"
        assert "address" in data
        assert data["address"]["addressLocality"] == home.city
        assert "contactPoint" in data
        assert data["foundingDate"] == "1975-01-01"


@pytest.mark.django_db
class TestTimelinePage:
    """Tests for TimelinePage model."""
    
    def test_timeline_creation(self, site):
        """Test timeline page creation."""
        home = HomePage.objects.first()
        
        timeline = TimelinePage(
            title="Timeline",
            slug="timeline",
            intro="La nostra storia",
        )
        home.add_child(instance=timeline)
        
        assert timeline.pk is not None
        assert timeline.intro == "La nostra storia"
    
    def test_timeline_schema_org_type(self, site):
        """Test timeline schema.org type is ItemList."""
        home = HomePage.objects.first()
        timeline = TimelinePage(title="Timeline", slug="timeline")
        home.add_child(instance=timeline)
        
        assert timeline.get_schema_org_type() == "ItemList"


@pytest.mark.django_db
class TestAboutPages:
    """Tests for About pages."""
    
    def test_about_page_subpage_types(self, site):
        """Test AboutPage allows correct subpage types."""
        assert "website.BoardPage" in AboutPage.subpage_types
        assert "website.TransparencyPage" in AboutPage.subpage_types
        assert "website.ContactPage" in AboutPage.subpage_types
    
    def test_contact_page_default_location(self, site):
        """Test ContactPage returns default location when not set."""
        home = HomePage.objects.first()
        unique_slug = f"chi-siamo-{uuid.uuid4().hex[:8]}"
        about = AboutPage(title="Chi Siamo", slug=unique_slug)
        home.add_child(instance=about)
        
        contact = ContactPage(
            title="Contatti",
            slug=f"contatti-{uuid.uuid4().hex[:8]}",
        )
        about.add_child(instance=contact)
        
        location = contact.get_map_location()
        
        assert location["lat"] == 45.0703
        assert location["lon"] == 7.6869
    
    def test_contact_page_custom_location(self, site):
        """Test ContactPage with custom coordinates."""
        home = HomePage.objects.first()
        unique_slug = f"chi-siamo-{uuid.uuid4().hex[:8]}"
        about = AboutPage(title="Chi Siamo", slug=unique_slug)
        home.add_child(instance=about)
        
        contact = ContactPage(
            title="Contatti",
            slug=f"contatti-{uuid.uuid4().hex[:8]}",
            latitude=44.0,
            longitude=8.0,
        )
        about.add_child(instance=contact)
        
        location = contact.get_map_location()
        
        assert location["lat"] == 44.0
        assert location["lon"] == 8.0


@pytest.mark.django_db
class TestEventPages:
    """Tests for Event pages."""
    
    def test_events_page_creation(self, site):
        """Test EventsPage creation."""
        home = HomePage.objects.first()
        
        events = EventsPage(
            title="Eventi",
            slug=f"eventi-{uuid.uuid4().hex[:8]}",
            intro="I nostri eventi",
        )
        home.add_child(instance=events)
        
        assert events.pk is not None
        assert events.get_schema_org_type() == "EventSeries"
    
    def test_event_detail_creation(self, site):
        """Test EventDetailPage creation."""
        home = HomePage.objects.first()
        events = EventsPage(title="Eventi", slug=f"eventi-{uuid.uuid4().hex[:8]}")
        home.add_child(instance=events)
        
        event = EventDetailPage(
            title="Raduno 2025",
            slug="raduno-2025",
            event_name="Raduno Moto 2025",
            start_date=datetime(2025, 6, 15, 10, 0),
            location_name="Piazza Castello",
            event_status="EventScheduled",
        )
        events.add_child(instance=event)
        
        assert event.pk is not None
        assert event.event_name == "Raduno Moto 2025"
        assert event.get_schema_org_type() == "Event"
    
    def test_event_detail_schema_org(self, site):
        """Test EventDetailPage schema.org data."""
        home = HomePage.objects.first()
        events = EventsPage(title="Eventi", slug=f"eventi-{uuid.uuid4().hex[:8]}")
        home.add_child(instance=events)
        
        event = EventDetailPage(
            title="Raduno 2025",
            slug="raduno-2025",
            event_name="Raduno Moto 2025",
            start_date=datetime(2025, 6, 15, 10, 0),
            location_name="Piazza Castello",
            location_address="Piazza Castello, Torino",
            event_status="EventScheduled",
        )
        events.add_child(instance=event)
        
        data = event.get_schema_org_data()
        
        assert data["name"] == "Raduno Moto 2025"
        assert "2025-06-15" in data["startDate"]
        assert data["location"]["name"] == "Piazza Castello"
        assert "EventScheduled" in data["eventStatus"]
        # Organizer ora usa SiteSettings, fallback a "MC Castellazzo Bormida"
        assert "MC Castellazzo" in data["organizer"]["name"]
