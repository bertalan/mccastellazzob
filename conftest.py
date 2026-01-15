"""
MC Castellazzo - Pytest Configuration
"""
import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure test database."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }


@pytest.fixture
def site(db):
    """Get or create Wagtail Site."""
    from wagtail.models import Site, Page
    from apps.website.models import HomePage
    import uuid
    
    # Check if homepage already exists
    existing_home = HomePage.objects.first()
    if existing_home:
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = existing_home
            site.save()
            return site
        return Site.objects.create(
            hostname="localhost",
            root_page=existing_home,
            is_default_site=True,
        )
    
    # Get root page
    root_page = Page.objects.filter(depth=1).first()
    if not root_page:
        root_page = Page.add_root(title="Root", slug="root")
    
    # Create homepage with unique slug
    unique_slug = f"home-{uuid.uuid4().hex[:8]}"
    home = HomePage(
        title="MC Castellazzo",
        slug=unique_slug,
        organization_name="MC Castellazzo",
        city="Torino",
        region="Piedmont",
        country="IT",
    )
    root_page.add_child(instance=home)
    
    # Get or create site
    site = Site.objects.filter(is_default_site=True).first()
    if site:
        site.root_page = home
        site.save()
    else:
        site = Site.objects.create(
            hostname="localhost",
            root_page=home,
            is_default_site=True,
        )
    
    return site


@pytest.fixture
def user(db):
    """Create test user."""
    from apps.custom_user.models import User
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    """Create admin user."""
    from apps.custom_user.models import User
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )
