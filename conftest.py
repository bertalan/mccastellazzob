"""
Pytest configuration and fixtures.

mccastellazzob.com - Moto Club Castellazzo Bormida
Fixtures globali per test suite.
"""

import pytest
from django.contrib.auth import get_user_model
from wagtail.models import Locale
from wagtail.models import Page
from wagtail.models import Site


User = get_user_model()


@pytest.fixture
def user(db):
    """Crea un utente base per i test."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db):
    """Crea un superuser per i test."""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def locale_it(db):
    """Crea o ottiene la locale italiana."""
    locale, _ = Locale.objects.get_or_create(language_code="it")
    return locale


@pytest.fixture
def locale_en(db):
    """Crea o ottiene la locale inglese."""
    locale, _ = Locale.objects.get_or_create(language_code="en")
    return locale


@pytest.fixture
def locale_fr(db):
    """Crea o ottiene la locale francese."""
    locale, _ = Locale.objects.get_or_create(language_code="fr")
    return locale


@pytest.fixture
def root_page(db, locale_it):
    """Ottiene o crea la root page."""
    try:
        return Page.objects.get(depth=1)
    except Page.DoesNotExist:
        root = Page.add_root(title="Root", slug="root")
        return root


@pytest.fixture
def site(db, root_page):
    """Crea o ottiene il sito principale."""
    site, _ = Site.objects.get_or_create(
        is_default_site=True,
        defaults={
            "hostname": "localhost",
            "root_page": root_page,
            "site_name": "Test Site",
        },
    )
    return site
