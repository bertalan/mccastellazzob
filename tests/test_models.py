"""
Test TDD per modifiche ai Models
=================================
Test per le nuove funzionalità dei models secondo PROPOSAL.md
"""
import pytest
from wagtail.models import Page, Site


@pytest.mark.django_db
class TestHomePageBody:
    """Test per HomePage.body StreamField."""
    
    def test_homepage_has_body_streamfield(self):
        """Test HomePage ha campo body StreamField."""
        from apps.website.models import HomePage
        from wagtail.fields import StreamField
        
        # Verifica che il campo body esista
        field = HomePage._meta.get_field("body")
        assert field is not None
    
    def test_homepage_body_allows_hero_slider(self):
        """Test HomePage body accetta HeroSliderBlock."""
        from apps.website.models import HomePage
        
        page = HomePage()
        body_field = page._meta.get_field("body")
        
        # Verifica che HeroSliderBlock sia nei block_types
        block_types = [b[0] for b in body_field.stream_block.child_blocks.items()]
        assert "hero_slider" in block_types
    
    def test_homepage_body_allows_hero_countdown(self):
        """Test HomePage body accetta HeroCountdownBlock."""
        from apps.website.models import HomePage
        
        page = HomePage()
        body_field = page._meta.get_field("body")
        block_types = [b[0] for b in body_field.stream_block.child_blocks.items()]
        assert "hero_countdown" in block_types
    
    def test_homepage_body_allows_stats(self):
        """Test HomePage body accetta StatsBlock."""
        from apps.website.models import HomePage
        
        page = HomePage()
        body_field = page._meta.get_field("body")
        block_types = [b[0] for b in body_field.stream_block.child_blocks.items()]
        assert "stats" in block_types
    
    def test_homepage_body_allows_section_cards(self):
        """Test HomePage body accetta SectionCardsGridBlock."""
        from apps.website.models import HomePage
        
        page = HomePage()
        body_field = page._meta.get_field("body")
        block_types = [b[0] for b in body_field.stream_block.child_blocks.items()]
        assert "section_cards" in block_types
    
    def test_homepage_body_allows_cta(self):
        """Test HomePage body accetta CTABlock."""
        from apps.website.models import HomePage
        
        page = HomePage()
        body_field = page._meta.get_field("body")
        block_types = [b[0] for b in body_field.stream_block.child_blocks.items()]
        assert "cta" in block_types


@pytest.mark.django_db
class TestAboutPageExtensions:
    """Test per AboutPage milestones e values."""
    
    def test_aboutpage_has_milestones(self):
        """Test AboutPage ha campo milestones StreamField."""
        from apps.website.models import AboutPage
        
        field = AboutPage._meta.get_field("milestones")
        assert field is not None
    
    def test_aboutpage_milestones_allows_stats(self):
        """Test AboutPage milestones accetta StatsBlock."""
        from apps.website.models import AboutPage
        
        page = AboutPage()
        field = page._meta.get_field("milestones")
        block_types = [b[0] for b in field.stream_block.child_blocks.items()]
        assert "stats" in block_types
    
    def test_aboutpage_has_values(self):
        """Test AboutPage ha campo values StreamField."""
        from apps.website.models import AboutPage
        
        field = AboutPage._meta.get_field("values")
        assert field is not None
    
    def test_aboutpage_values_allows_values_block(self):
        """Test AboutPage values accetta ValuesBlock."""
        from apps.website.models import AboutPage
        
        page = AboutPage()
        field = page._meta.get_field("values")
        block_types = [b[0] for b in field.stream_block.child_blocks.items()]
        assert "values" in block_types


@pytest.mark.django_db
class TestEventsPageFeatured:
    """Test per EventsPage featured_event."""
    
    def test_eventspage_has_featured_event(self):
        """Test EventsPage ha campo featured_event."""
        from apps.website.models import EventsPage
        
        field = EventsPage._meta.get_field("featured_event")
        assert field is not None
    
    def test_eventspage_featured_event_is_page_chooser(self):
        """Test featured_event è un PageChooserBlock/ForeignKey."""
        from apps.website.models import EventsPage
        from django.db.models import ForeignKey
        
        field = EventsPage._meta.get_field("featured_event")
        assert isinstance(field, ForeignKey)
    
    def test_eventspage_has_hero_section(self):
        """Test EventsPage ha campo hero StreamField."""
        from apps.website.models import EventsPage
        
        field = EventsPage._meta.get_field("hero")
        assert field is not None


@pytest.mark.django_db
class TestGalleryPage:
    """Test per nuovo GalleryPage model."""
    
    def test_gallerypage_exists(self):
        """Test GalleryPage model esiste."""
        from apps.website.models import GalleryPage
        
        assert GalleryPage is not None
    
    def test_gallerypage_inherits_from_page(self):
        """Test GalleryPage eredita da Page."""
        from apps.website.models import GalleryPage
        from wagtail.models import Page
        
        assert issubclass(GalleryPage, Page)
    
    def test_gallerypage_has_gallery_streamfield(self):
        """Test GalleryPage ha campo gallery."""
        from apps.website.models import GalleryPage
        
        field = GalleryPage._meta.get_field("gallery")
        assert field is not None
    
    def test_gallerypage_gallery_allows_gallery_block(self):
        """Test GalleryPage gallery accetta GalleryBlock."""
        from apps.website.models import GalleryPage
        
        page = GalleryPage()
        field = page._meta.get_field("gallery")
        block_types = [b[0] for b in field.stream_block.child_blocks.items()]
        assert "gallery" in block_types
    
    def test_gallerypage_has_intro(self):
        """Test GalleryPage ha campo intro."""
        from apps.website.models import GalleryPage
        
        field = GalleryPage._meta.get_field("intro")
        assert field is not None
    
    def test_gallerypage_has_template(self):
        """Test GalleryPage ha template definito."""
        from apps.website.models import GalleryPage
        
        assert GalleryPage.template == "website/pages/gallery_page.jinja2"


@pytest.mark.django_db
class TestModelIntegration:
    """Test di integrazione con database."""
    
    def test_homepage_body_can_be_saved(self, site):
        """Test HomePage body può essere salvato."""
        from apps.website.models import HomePage
        
        root = site.root_page
        homepage = HomePage(
            title="Test Home",
            slug="test-home",
            body=[
                {"type": "stats", "value": {
                    "stats": [
                        {"icon": "fas fa-star", "icon_bg_color": "bg-gold", "value": "50+", "label": "Anni"},
                        {"icon": "fas fa-users", "icon_bg_color": "bg-bordeaux", "value": "100", "label": "Soci"},
                    ],
                    "background": "bg-white",
                }},
            ],
        )
        root.add_child(instance=homepage)
        
        # Verifica salvato correttamente
        saved_page = HomePage.objects.get(pk=homepage.pk)
        assert len(saved_page.body) == 1
        assert saved_page.body[0].block_type == "stats"
    
    def test_gallerypage_can_be_created(self, site):
        """Test GalleryPage può essere creato."""
        from apps.website.models import GalleryPage
        
        root = site.root_page
        gallery = GalleryPage(
            title="Galleria Test",
            slug="galleria-test",
            intro="Galleria di prova",
        )
        root.add_child(instance=gallery)
        
        saved_page = GalleryPage.objects.get(pk=gallery.pk)
        assert saved_page.title == "Galleria Test"
