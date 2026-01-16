"""
Test TDD per Homepage Carousel
==============================
Integrazione con Carousel di CodeRedCMS per lo slider della homepage.
"""
import pytest
from django.db import models
from wagtail.models import Page


@pytest.mark.django_db
class TestHomePageCarousel:
    """Test per l'integrazione del Carousel nella HomePage."""

    def test_homepage_has_hero_carousel_field(self):
        """Test HomePage ha campo hero_carousel ForeignKey."""
        from apps.website.models import HomePage
        
        field = HomePage._meta.get_field("hero_carousel")
        assert field is not None
        assert isinstance(field, models.ForeignKey)

    def test_hero_carousel_references_coderedcms_carousel(self):
        """Test hero_carousel referenzia coderedcms.Carousel."""
        from apps.website.models import HomePage
        from coderedcms.models import Carousel
        
        field = HomePage._meta.get_field("hero_carousel")
        assert field.remote_field.model == Carousel

    def test_hero_carousel_is_optional(self):
        """Test hero_carousel è opzionale (null=True, blank=True)."""
        from apps.website.models import HomePage
        
        field = HomePage._meta.get_field("hero_carousel")
        assert field.null is True
        assert field.blank is True

    def test_hero_carousel_on_delete_set_null(self):
        """Test hero_carousel usa SET_NULL on_delete."""
        from apps.website.models import HomePage
        
        field = HomePage._meta.get_field("hero_carousel")
        assert field.remote_field.on_delete == models.SET_NULL

    def test_hero_carousel_in_content_panels(self):
        """Test hero_carousel è nei content_panels della HomePage."""
        from apps.website.models import HomePage
        
        panel_names = []
        for panel in HomePage.content_panels:
            if hasattr(panel, 'field_name'):
                panel_names.append(panel.field_name)
            elif hasattr(panel, 'children'):
                for child in panel.children:
                    if hasattr(child, 'field_name'):
                        panel_names.append(child.field_name)
        
        assert "hero_carousel" in panel_names


@pytest.mark.django_db
class TestCarouselIntegration:
    """Test per la creazione e uso del Carousel."""

    def test_can_create_carousel_with_slides(self):
        """Test creazione Carousel con slides."""
        from coderedcms.models import Carousel, CarouselSlide
        
        carousel = Carousel.objects.create(
            name="Homepage Slider",
            show_controls=True,
            show_indicators=True,
        )
        
        # Carousel senza slide inizialmente
        assert carousel.carousel_slides.count() == 0
        assert carousel.name == "Homepage Slider"

    def test_carousel_has_show_controls_field(self):
        """Test Carousel ha campo show_controls."""
        from coderedcms.models import Carousel
        
        field = Carousel._meta.get_field("show_controls")
        assert field is not None

    def test_carousel_has_show_indicators_field(self):
        """Test Carousel ha campo show_indicators."""
        from coderedcms.models import Carousel
        
        field = Carousel._meta.get_field("show_indicators")
        assert field is not None


@pytest.mark.django_db
class TestHomepageWithCarousel:
    """Test per Homepage con Carousel associato."""

    def test_homepage_can_have_carousel(self):
        """Test HomePage può avere un Carousel associato."""
        from apps.website.models import HomePage
        from coderedcms.models import Carousel
        from wagtail.models import Page
        
        # Crea carousel
        carousel = Carousel.objects.create(
            name="Test Slider",
            show_controls=True,
            show_indicators=True,
        )
        
        # Verifica che il campo esiste e può essere assegnato
        homepage = HomePage()
        homepage.hero_carousel = carousel
        assert homepage.hero_carousel == carousel
        assert homepage.hero_carousel.name == "Test Slider"
