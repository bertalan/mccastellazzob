"""
MC Castellazzo - StreamField Blocks Tests (TDD)
================================================
Test per i nuovi blocks grafici.
"""
import pytest
from django.test import TestCase
from wagtail import blocks

from apps.website.blocks import (
    # Nuovi blocks da implementare
    HeroSlideBlock,
    HeroSliderBlock,
    HeroCountdownBlock,
    StatItemBlock,
    StatsBlock,
    SectionCardBlock,
    SectionCardsGridBlock,
    CTABlock,
    ValueItemBlock,
    ValuesBlock,
    # Blocks esistenti da estendere
    GalleryImageBlock,
    GalleryBlock,
)


@pytest.mark.django_db
class TestHeroSliderBlock:
    """Tests for HeroSliderBlock."""
    
    def test_hero_slide_block_fields(self):
        """Test HeroSlideBlock has required fields."""
        block = HeroSlideBlock()
        
        assert "image" in block.child_blocks
        assert "title" in block.child_blocks
        assert "category" in block.child_blocks
        assert "link" in block.child_blocks
    
    def test_hero_slider_block_fields(self):
        """Test HeroSliderBlock has required fields."""
        block = HeroSliderBlock()
        
        assert "slides" in block.child_blocks
        assert "autoplay" in block.child_blocks
        assert "interval" in block.child_blocks
        assert "height" in block.child_blocks
    
    def test_hero_slider_default_values(self):
        """Test HeroSliderBlock default values."""
        block = HeroSliderBlock()
        
        # Check defaults - uso get_default() per BooleanBlock
        assert block.child_blocks["autoplay"].get_default() is True
        assert block.child_blocks["interval"].get_default() == 5000
        assert block.child_blocks["height"].get_default() == "75vh"
    
    def test_hero_slider_has_template(self):
        """Test HeroSliderBlock has template defined."""
        block = HeroSliderBlock()
        assert block.meta.template == "website/blocks/hero_slider_block.html"


@pytest.mark.django_db
class TestHeroCountdownBlock:
    """Tests for HeroCountdownBlock."""
    
    def test_hero_countdown_block_fields(self):
        """Test HeroCountdownBlock has required fields."""
        block = HeroCountdownBlock()
        
        assert "badge_text" in block.child_blocks
        assert "title" in block.child_blocks
        assert "title_highlight" in block.child_blocks
        assert "subtitle" in block.child_blocks
        assert "cta_primary_text" in block.child_blocks
        assert "cta_primary_link" in block.child_blocks
        assert "event" in block.child_blocks
        assert "show_countdown" in block.child_blocks
    
    def test_hero_countdown_has_template(self):
        """Test HeroCountdownBlock has template defined."""
        block = HeroCountdownBlock()
        assert block.meta.template == "website/blocks/hero_countdown_block.html"


@pytest.mark.django_db
class TestStatsBlock:
    """Tests for StatsBlock."""
    
    def test_stat_item_block_fields(self):
        """Test StatItemBlock has required fields."""
        block = StatItemBlock()
        
        assert "icon" in block.child_blocks
        assert "icon_bg_color" in block.child_blocks
        assert "value" in block.child_blocks
        assert "label" in block.child_blocks
    
    def test_stats_block_fields(self):
        """Test StatsBlock has required fields."""
        block = StatsBlock()
        
        assert "stats" in block.child_blocks
        assert "background" in block.child_blocks
    
    def test_stats_block_has_template(self):
        """Test StatsBlock has template defined."""
        block = StatsBlock()
        assert block.meta.template == "website/blocks/stats_block.html"


@pytest.mark.django_db
class TestSectionCardsBlock:
    """Tests for SectionCardBlock and SectionCardsGridBlock."""
    
    def test_section_card_block_fields(self):
        """Test SectionCardBlock has required fields."""
        block = SectionCardBlock()
        
        assert "title" in block.child_blocks
        assert "description" in block.child_blocks
        assert "image" in block.child_blocks
        assert "icon" in block.child_blocks
        assert "icon_bg_color" in block.child_blocks
        assert "link_page" in block.child_blocks
        assert "link_text" in block.child_blocks
    
    def test_section_cards_grid_block_fields(self):
        """Test SectionCardsGridBlock has required fields."""
        block = SectionCardsGridBlock()
        
        assert "heading_label" in block.child_blocks
        assert "heading_title" in block.child_blocks
        assert "heading_subtitle" in block.child_blocks
        assert "cards" in block.child_blocks
        assert "layout" in block.child_blocks
    
    def test_section_cards_grid_has_template(self):
        """Test SectionCardsGridBlock has template defined."""
        block = SectionCardsGridBlock()
        assert block.meta.template == "website/blocks/section_cards_grid_block.html"


@pytest.mark.django_db
class TestCTABlock:
    """Tests for CTABlock."""
    
    def test_cta_block_fields(self):
        """Test CTABlock has required fields."""
        block = CTABlock()
        
        assert "title" in block.child_blocks
        assert "title_highlight" in block.child_blocks
        assert "subtitle" in block.child_blocks
        assert "cta_primary_text" in block.child_blocks
        assert "cta_primary_link" in block.child_blocks
        assert "cta_primary_icon" in block.child_blocks
        assert "cta_secondary_text" in block.child_blocks
        assert "cta_secondary_link" in block.child_blocks
        assert "background" in block.child_blocks
    
    def test_cta_block_has_template(self):
        """Test CTABlock has template defined."""
        block = CTABlock()
        assert block.meta.template == "website/blocks/cta_block.html"


@pytest.mark.django_db
class TestValuesBlock:
    """Tests for ValuesBlock."""
    
    def test_value_item_block_fields(self):
        """Test ValueItemBlock has required fields."""
        block = ValueItemBlock()
        
        assert "icon" in block.child_blocks
        assert "title" in block.child_blocks
        assert "description" in block.child_blocks
    
    def test_values_block_fields(self):
        """Test ValuesBlock has required fields."""
        block = ValuesBlock()
        
        assert "heading" in block.child_blocks
        assert "values" in block.child_blocks
    
    def test_values_block_has_template(self):
        """Test ValuesBlock has template defined."""
        block = ValuesBlock()
        assert block.meta.template == "website/blocks/values_block.html"


@pytest.mark.django_db
class TestGalleryBlockExtended:
    """Tests for extended GalleryBlock with categories."""
    
    def test_gallery_image_block_has_category(self):
        """Test GalleryImageBlock has category field."""
        block = GalleryImageBlock()
        
        assert "category" in block.child_blocks
    
    def test_gallery_block_has_filters(self):
        """Test GalleryBlock has show_filters field."""
        block = GalleryBlock()
        
        assert "show_filters" in block.child_blocks
        assert "columns" in block.child_blocks
    
    def test_gallery_category_choices(self):
        """Test GalleryImageBlock category choices."""
        block = GalleryImageBlock()
        category_block = block.child_blocks["category"]
        
        # ChoiceBlock._constructor_kwargs contiene le choices originali
        choices = [c[0] for c in category_block._constructor_kwargs["choices"]]
        assert "all" in choices
        assert "raduni" in choices
        assert "escursioni" in choices
        assert "gare" in choices
        assert "sociali" in choices
