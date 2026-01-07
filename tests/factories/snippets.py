"""
Snippet factories.

mccastellazzob.com - Moto Club Castellazzo Bormida
Factories per Navbar e Footer.
"""

import factory
from wagtail.models import Locale

from apps.website.models.snippets import Footer
from apps.website.models.snippets import Navbar


class NavbarFactory(factory.django.DjangoModelFactory):
    """Factory per creare Navbar."""

    class Meta:
        model = Navbar

    name = factory.Sequence(lambda n: f"Navbar {n}")

    @factory.lazy_attribute
    def locale(self):
        """Ottiene o crea la locale italiana di default."""
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class NavbarITFactory(NavbarFactory):
    """Factory per Navbar italiana."""

    name = factory.Sequence(lambda n: f"Navbar IT {n}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class NavbarENFactory(NavbarFactory):
    """Factory per Navbar inglese."""

    name = factory.Sequence(lambda n: f"Navbar EN {n}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="en")
        return locale


class FooterFactory(factory.django.DjangoModelFactory):
    """Factory per creare Footer."""

    class Meta:
        model = Footer

    name = factory.Sequence(lambda n: f"Footer {n}")

    @factory.lazy_attribute
    def locale(self):
        """Ottiene o crea la locale italiana di default."""
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class FooterITFactory(FooterFactory):
    """Factory per Footer italiano."""

    name = factory.Sequence(lambda n: f"Footer IT {n}")


class FooterENFactory(FooterFactory):
    """Factory per Footer inglese."""

    name = factory.Sequence(lambda n: f"Footer EN {n}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="en")
        return locale
