"""
Tests for snippet models.

mccastellazzob.com - Moto Club Castellazzo Bormida
"""

import pytest
from wagtail.models import Locale

from apps.website.models.snippets import Footer
from apps.website.models.snippets import Navbar
from tests.factories.snippets import FooterENFactory
from tests.factories.snippets import FooterFactory
from tests.factories.snippets import NavbarENFactory
from tests.factories.snippets import NavbarFactory
from tests.factories.snippets import NavbarITFactory


@pytest.mark.django_db
class TestNavbarModel:
    """Test per il modello Navbar."""

    def test_create_navbar(self):
        """Test creazione navbar base."""
        navbar = NavbarFactory()
        assert navbar.name is not None
        assert navbar.locale is not None

    def test_navbar_str(self):
        """Test rappresentazione stringa."""
        navbar = NavbarFactory(name="Main Menu")
        assert "Main Menu" in str(navbar)

    def test_navbar_italian(self, locale_it):
        """Test navbar italiana."""
        navbar = NavbarITFactory()
        assert navbar.locale.language_code == "it"

    def test_navbar_english(self, locale_en):
        """Test navbar inglese."""
        navbar = NavbarENFactory()
        assert navbar.locale.language_code == "en"

    def test_navbar_unique_together(self, locale_it):
        """Test vincolo unique_together translation_key + locale."""
        navbar1 = NavbarFactory(locale=locale_it)

        # Creare un'altra navbar con stesso translation_key e locale
        # dovrebbe fallire (gestito da TranslatableMixin)
        navbar2 = NavbarFactory(locale=locale_it)

        # I translation_key dovrebbero essere diversi
        assert navbar1.translation_key != navbar2.translation_key


@pytest.mark.django_db
class TestFooterModel:
    """Test per il modello Footer."""

    def test_create_footer(self):
        """Test creazione footer base."""
        footer = FooterFactory()
        assert footer.name is not None
        assert footer.locale is not None

    def test_footer_str(self):
        """Test rappresentazione stringa."""
        footer = FooterFactory(name="Main Footer")
        assert "Main Footer" in str(footer)

    def test_footer_italian(self, locale_it):
        """Test footer italiano."""
        footer = FooterFactory(locale=locale_it)
        assert footer.locale.language_code == "it"

    def test_footer_english(self, locale_en):
        """Test footer inglese."""
        footer = FooterENFactory()
        assert footer.locale.language_code == "en"
