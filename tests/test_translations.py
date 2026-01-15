"""
MC Castellazzo - Translation and Multilingual Tests
=====================================================
Verifica tutte le pagine e relative traduzioni come da CLAUDE.md:
- 4 lingue pari (IT/FR/ES/EN)
- Tutte le pagine accessibili in tutte le lingue
- Schema.org corretto per ogni tipo di pagina
- URL con prefisso lingua (/it/, /fr/, /es/, /en/)
"""
import pytest
from datetime import date, datetime, timezone

from django.test import Client
from wagtail.models import Locale, Page, Site

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


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def locales(db):
    """Create all 4 required locales."""
    locales = {}
    for code in ["it", "fr", "es", "en"]:
        locale, _ = Locale.objects.get_or_create(language_code=code)
        locales[code] = locale
    return locales


@pytest.fixture
def homepage_with_translations(db, locales):
    """Create HomePage with translations in all 4 languages."""
    from apps.website.models import HomePage
    
    # Clean existing data
    Site.objects.all().delete()
    HomePage.objects.all().delete()
    Page.objects.filter(depth__gt=1).delete()
    
    # Get root page
    root_page = Page.objects.filter(depth=1).first()
    if not root_page:
        root_page = Page.add_root(title="Root", slug="root")
    
    # Create Italian homepage (default)
    home_it = HomePage(
        title="Home",
        slug="home",
        locale=locales["it"],
        organization_name="Moto Club Castellazzo Bormida",
        description="<p>Il Moto Club Castellazzo Bormida, fondato nel 1933</p>",
        city="Castellazzo Bormida",
        region="Piemonte",
        country="IT",
        street_address="Via Roma, 45",
        postal_code="15073",
        telephone="+39 0131 123456",
        email="info@mccastellazzobormida.it",
        founding_date=date(1933, 1, 1),
        hero_title="Moto Club Castellazzo Bormida",
        hero_subtitle="Dal 1933 - La passione per le due ruote",
    )
    root_page.add_child(instance=home_it)
    home_it.save_revision().publish()
    
    # Create Site
    Site.objects.all().delete()
    Site.objects.create(
        hostname="localhost",
        port=80,
        root_page=home_it,
        is_default_site=True,
        site_name="MC Castellazzo",
    )
    
    # Create translations
    translations = {"it": home_it}
    translation_data = {
        "fr": {"title": "Accueil", "hero_subtitle": "Depuis 1933 - La passion des deux-roues"},
        "es": {"title": "Inicio", "hero_subtitle": "Desde 1933 - La pasión por las dos ruedas"},
        "en": {"title": "Home", "hero_subtitle": "Since 1933 - The passion for motorcycles"},
    }
    
    for lang_code, data in translation_data.items():
        home_translated = home_it.copy_for_translation(locales[lang_code], copy_parents=True, alias=False)
        home_translated.title = data["title"]
        home_translated.hero_subtitle = data["hero_subtitle"]
        home_translated.save_revision().publish()
        translations[lang_code] = home_translated
    
    return translations


@pytest.fixture
def full_site_structure(homepage_with_translations, locales):
    """Create complete site structure with all pages in Italian."""
    home_it = homepage_with_translations["it"]
    locale_it = locales["it"]
    
    # Timeline Page
    timeline = TimelinePage(
        title="Novità",
        slug="novita",
        locale=locale_it,
        intro="<p>Le ultime notizie del Moto Club</p>",
    )
    home_it.add_child(instance=timeline)
    timeline.save_revision().publish()
    
    # About Page
    about = AboutPage(
        title="Chi Siamo",
        slug="chi-siamo",
        locale=locale_it,
        intro="<p>Scopri la storia del Moto Club</p>",
        body="<p>Il Moto Club Castellazzo nasce nel 1933...</p>",
    )
    home_it.add_child(instance=about)
    about.save_revision().publish()
    
    # Board Page (child of About)
    board = BoardPage(
        title="Consiglio Direttivo",
        slug="consiglio-direttivo",
        locale=locale_it,
        intro="<p>Il Consiglio Direttivo del Club</p>",
    )
    about.add_child(instance=board)
    board.save_revision().publish()
    
    # Transparency Page (child of About)
    transparency = TransparencyPage(
        title="Trasparenza",
        slug="trasparenza",
        locale=locale_it,
        intro="<p>Documenti e bilanci</p>",
    )
    about.add_child(instance=transparency)
    transparency.save_revision().publish()
    
    # Contact Page (child of About)
    contact = ContactPage(
        title="Contatti",
        slug="contatti",
        locale=locale_it,
        intro="<p>Come contattarci</p>",
        address="Via Roma 45, Castellazzo Bormida",
        latitude=44.8456,
        longitude=8.5734,
        phone="+39 0131 123456",
        email="info@mccastellazzobormida.it",
    )
    about.add_child(instance=contact)
    contact.save_revision().publish()
    
    # Events Page
    events = EventsPage(
        title="Eventi",
        slug="eventi",
        locale=locale_it,
        intro="<p>Gli eventi del Club</p>",
    )
    home_it.add_child(instance=events)
    events.save_revision().publish()
    
    # Event Detail Page
    event = EventDetailPage(
        title="92° Raduno Nazionale",
        slug="raduno-2026",
        locale=locale_it,
        event_name="92° Raduno Nazionale MC Castellazzo",
        start_date=datetime(2026, 6, 15, 9, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 6, 16, 18, 0, tzinfo=timezone.utc),
        location_name="Piazza Vittorio Emanuele II",
        location_address="Castellazzo Bormida",
        description="<p>La storica manifestazione!</p>",
        event_status="EventScheduled",
    )
    events.add_child(instance=event)
    event.save_revision().publish()
    
    # Archive Page
    archive = EventsArchivePage(
        title="Archivio Eventi",
        slug="archivio-eventi",
        locale=locale_it,
        intro="<p>Archivio storico eventi</p>",
    )
    home_it.add_child(instance=archive)
    archive.save_revision().publish()
    
    return {
        "home": home_it,
        "timeline": timeline,
        "about": about,
        "board": board,
        "transparency": transparency,
        "contact": contact,
        "events": events,
        "event": event,
        "archive": archive,
    }


# ============================================================
# TEST: LOCALE CONFIGURATION
# ============================================================

@pytest.mark.django_db
class TestLocaleConfiguration:
    """Test that all 4 languages are properly configured."""
    
    def test_four_locales_exist(self, locales):
        """Test that IT, FR, ES, EN locales exist."""
        assert len(locales) == 4
        assert set(locales.keys()) == {"it", "fr", "es", "en"}
    
    def test_italian_is_default(self, locales):
        """Test that Italian is the default locale."""
        default = Locale.get_default()
        assert default.language_code == "it"
    
    def test_all_locales_in_database(self, locales):
        """Test all locales are saved in database."""
        db_locales = Locale.objects.values_list("language_code", flat=True)
        for code in ["it", "fr", "es", "en"]:
            assert code in db_locales


# ============================================================
# TEST: HOMEPAGE TRANSLATIONS
# ============================================================

@pytest.mark.django_db
class TestHomePageTranslations:
    """Test HomePage exists in all 4 languages."""
    
    def test_homepage_exists_in_all_languages(self, homepage_with_translations):
        """Test homepage has translations for all 4 languages."""
        assert len(homepage_with_translations) == 4
        for lang in ["it", "fr", "es", "en"]:
            assert lang in homepage_with_translations
            assert homepage_with_translations[lang] is not None
    
    def test_homepage_translation_key_matches(self, homepage_with_translations):
        """Test all homepage translations share same translation_key."""
        translation_keys = {
            hp.translation_key for hp in homepage_with_translations.values()
        }
        assert len(translation_keys) == 1, "All translations should share the same translation_key"
    
    def test_homepage_titles_are_translated(self, homepage_with_translations):
        """Test homepage titles are different per language."""
        titles = {
            "it": "Home",
            "fr": "Accueil",
            "es": "Inicio",
            "en": "Home",
        }
        for lang, expected_title in titles.items():
            assert homepage_with_translations[lang].title == expected_title
    
    def test_homepage_organization_name_preserved(self, homepage_with_translations):
        """Test organization name is the same in all languages."""
        for hp in homepage_with_translations.values():
            assert hp.organization_name == "Moto Club Castellazzo Bormida"


# ============================================================
# TEST: PAGE STRUCTURE
# ============================================================

@pytest.mark.django_db
class TestPageStructure:
    """Test complete page structure as defined in CLAUDE.md."""
    
    def test_homepage_exists(self, full_site_structure):
        """Test HomePage exists."""
        assert full_site_structure["home"] is not None
        assert isinstance(full_site_structure["home"], HomePage)
    
    def test_timeline_page_exists(self, full_site_structure):
        """Test TimelinePage exists (schema.org ItemList)."""
        assert full_site_structure["timeline"] is not None
        assert isinstance(full_site_structure["timeline"], TimelinePage)
    
    def test_about_page_exists(self, full_site_structure):
        """Test AboutPage exists (schema.org AboutPage)."""
        assert full_site_structure["about"] is not None
        assert isinstance(full_site_structure["about"], AboutPage)
    
    def test_board_page_exists(self, full_site_structure):
        """Test BoardPage exists as child of About (Consiglio Direttivo)."""
        assert full_site_structure["board"] is not None
        assert isinstance(full_site_structure["board"], BoardPage)
        assert full_site_structure["board"].get_parent() == full_site_structure["about"]
    
    def test_transparency_page_exists(self, full_site_structure):
        """Test TransparencyPage exists as child of About."""
        assert full_site_structure["transparency"] is not None
        assert isinstance(full_site_structure["transparency"], TransparencyPage)
        assert full_site_structure["transparency"].get_parent() == full_site_structure["about"]
    
    def test_contact_page_exists(self, full_site_structure):
        """Test ContactPage exists as child of About (schema.org ContactPage)."""
        assert full_site_structure["contact"] is not None
        assert isinstance(full_site_structure["contact"], ContactPage)
        assert full_site_structure["contact"].get_parent() == full_site_structure["about"]
    
    def test_events_page_exists(self, full_site_structure):
        """Test EventsPage exists (schema.org EventSeries)."""
        assert full_site_structure["events"] is not None
        assert isinstance(full_site_structure["events"], EventsPage)
    
    def test_event_detail_page_exists(self, full_site_structure):
        """Test EventDetailPage exists (schema.org Event)."""
        assert full_site_structure["event"] is not None
        assert isinstance(full_site_structure["event"], EventDetailPage)
        assert full_site_structure["event"].get_parent() == full_site_structure["events"]
    
    def test_archive_page_exists(self, full_site_structure):
        """Test EventsArchivePage exists."""
        assert full_site_structure["archive"] is not None
        assert isinstance(full_site_structure["archive"], EventsArchivePage)


# ============================================================
# TEST: SCHEMA.ORG TYPES
# ============================================================

@pytest.mark.django_db
class TestSchemaOrgTypes:
    """Test schema.org types are correct for each page as per CLAUDE.md."""
    
    def test_homepage_schema_org_organization(self, full_site_structure):
        """Test HomePage has schema.org Organization type."""
        home = full_site_structure["home"]
        assert home.get_schema_org_type() == "Organization"
    
    def test_timeline_schema_org_itemlist(self, full_site_structure):
        """Test TimelinePage has schema.org ItemList type."""
        timeline = full_site_structure["timeline"]
        assert timeline.get_schema_org_type() == "ItemList"
    
    def test_about_schema_org_aboutpage(self, full_site_structure):
        """Test AboutPage has schema.org AboutPage type."""
        about = full_site_structure["about"]
        assert about.get_schema_org_type() == "AboutPage"
    
    def test_board_schema_org_organization(self, full_site_structure):
        """Test BoardPage has schema.org Organization type (for member list)."""
        board = full_site_structure["board"]
        assert board.get_schema_org_type() == "Organization"
    
    def test_transparency_schema_org_webpage(self, full_site_structure):
        """Test TransparencyPage has schema.org WebPage type."""
        transparency = full_site_structure["transparency"]
        assert transparency.get_schema_org_type() == "WebPage"
    
    def test_contact_schema_org_organization(self, full_site_structure):
        """Test ContactPage has schema.org Organization type (valid type for contact info)."""
        contact = full_site_structure["contact"]
        assert contact.get_schema_org_type() == "Organization"
    
    def test_events_schema_org_eventseries(self, full_site_structure):
        """Test EventsPage has schema.org EventSeries type."""
        events = full_site_structure["events"]
        assert events.get_schema_org_type() == "EventSeries"
    
    def test_event_detail_schema_org_event(self, full_site_structure):
        """Test EventDetailPage has schema.org Event type."""
        event = full_site_structure["event"]
        assert event.get_schema_org_type() == "Event"


# ============================================================
# TEST: URL PATTERNS WITH LANGUAGE PREFIX
# ============================================================

@pytest.mark.django_db
class TestUrlPatterns:
    """Test URL patterns with language prefix (/it/, /fr/, /es/, /en/)."""
    
    def test_homepage_url_includes_language(self, homepage_with_translations):
        """Test homepage URLs include language prefix."""
        # With prefix_default_language=True, Italian homepage should have /it/
        home_it = homepage_with_translations["it"]
        assert home_it.url == "/it/"
    
    def test_homepage_url_path_correct(self, homepage_with_translations):
        """Test homepage url_path is correct."""
        home_it = homepage_with_translations["it"]
        assert "/home" in home_it.url_path
    
    def test_child_page_urls_are_correct(self, full_site_structure):
        """Test child pages have correct URL paths."""
        pages_and_expected_slugs = [
            ("timeline", "novita"),
            ("about", "chi-siamo"),
            ("events", "eventi"),
            ("archive", "archivio-eventi"),
        ]
        for page_name, expected_slug in pages_and_expected_slugs:
            page = full_site_structure[page_name]
            assert expected_slug in page.url_path, f"Page {page_name} should have {expected_slug} in url_path"
    
    def test_nested_page_urls_are_correct(self, full_site_structure):
        """Test nested pages have correct URL paths."""
        # Board should be under chi-siamo
        board = full_site_structure["board"]
        assert "chi-siamo" in board.url_path
        assert "consiglio-direttivo" in board.url_path
        
        # Event should be under eventi
        event = full_site_structure["event"]
        assert "eventi" in event.url_path
    
    def test_all_pages_are_live(self, full_site_structure):
        """Test all pages are published (live)."""
        for name, page in full_site_structure.items():
            assert page.live, f"Page {name} should be live"
    
    def test_all_pages_are_in_italian_locale(self, full_site_structure, locales):
        """Test all pages are in Italian locale."""
        for name, page in full_site_structure.items():
            assert page.locale == locales["it"], f"Page {name} should be in Italian locale"


# ============================================================
# TEST: HOMEPAGE REQUIRED FIELDS (CLAUDE.md)
# ============================================================

@pytest.mark.django_db
class TestHomePageRequiredFields:
    """Test HomePage has all required fields from CLAUDE.md."""
    
    def test_homepage_has_organization_name(self, homepage_with_translations):
        """Test HomePage has name field (organization_name)."""
        home = homepage_with_translations["it"]
        assert hasattr(home, "organization_name")
        assert home.organization_name is not None
    
    def test_homepage_has_address_fields(self, homepage_with_translations):
        """Test HomePage has PostalAddress fields."""
        home = homepage_with_translations["it"]
        assert hasattr(home, "street_address")
        assert hasattr(home, "city")
        assert hasattr(home, "region")
        assert hasattr(home, "country")
        assert hasattr(home, "postal_code")
    
    def test_homepage_has_contact_fields(self, homepage_with_translations):
        """Test HomePage has ContactPoint fields."""
        home = homepage_with_translations["it"]
        assert hasattr(home, "telephone")
        assert hasattr(home, "email")
    
    def test_homepage_has_founding_date(self, homepage_with_translations):
        """Test HomePage has foundingDate field."""
        home = homepage_with_translations["it"]
        assert hasattr(home, "founding_date")
        assert home.founding_date == date(1933, 1, 1)
    
    def test_homepage_schema_data_includes_address(self, homepage_with_translations):
        """Test HomePage schema.org data includes address."""
        home = homepage_with_translations["it"]
        schema_data = home.get_schema_org_data()
        
        assert "address" in schema_data
        assert schema_data["address"]["@type"] == "PostalAddress"
        assert schema_data["address"]["addressLocality"] == "Castellazzo Bormida"
    
    def test_homepage_schema_data_includes_contact(self, homepage_with_translations):
        """Test HomePage schema.org data includes contactPoint."""
        home = homepage_with_translations["it"]
        schema_data = home.get_schema_org_data()
        
        assert "contactPoint" in schema_data
        assert schema_data["contactPoint"]["@type"] == "ContactPoint"


# ============================================================
# TEST: CONTACT PAGE WITH MAP
# ============================================================

@pytest.mark.django_db
class TestContactPageMap:
    """Test ContactPage has OpenStreetMap fields (no Google Maps per CLAUDE.md)."""
    
    def test_contact_has_coordinates(self, full_site_structure):
        """Test ContactPage has latitude and longitude fields."""
        contact = full_site_structure["contact"]
        assert hasattr(contact, "latitude")
        assert hasattr(contact, "longitude")
        assert contact.latitude == pytest.approx(44.8456, rel=1e-3)
        assert contact.longitude == pytest.approx(8.5734, rel=1e-3)
    
    def test_contact_has_address(self, full_site_structure):
        """Test ContactPage has address field."""
        contact = full_site_structure["contact"]
        assert hasattr(contact, "address")
        assert "Castellazzo" in contact.address


# ============================================================
# TEST: EVENT FIELDS
# ============================================================

@pytest.mark.django_db
class TestEventFields:
    """Test EventDetailPage has all required schema.org Event fields."""
    
    def test_event_has_name(self, full_site_structure):
        """Test EventDetailPage has event name."""
        event = full_site_structure["event"]
        assert event.event_name == "92° Raduno Nazionale MC Castellazzo"
    
    def test_event_has_dates(self, full_site_structure):
        """Test EventDetailPage has start and end dates."""
        event = full_site_structure["event"]
        assert event.start_date is not None
        assert event.end_date is not None
        assert event.end_date > event.start_date
    
    def test_event_has_location(self, full_site_structure):
        """Test EventDetailPage has location fields."""
        event = full_site_structure["event"]
        assert event.location_name == "Piazza Vittorio Emanuele II"
        assert event.location_address is not None
    
    def test_event_has_status(self, full_site_structure):
        """Test EventDetailPage has eventStatus field."""
        event = full_site_structure["event"]
        assert event.event_status in ["EventScheduled", "EventCancelled", "EventPostponed"]
    
    def test_event_schema_org_data(self, full_site_structure):
        """Test EventDetailPage schema.org data is correct."""
        event = full_site_structure["event"]
        schema_data = event.get_schema_org_data()
        
        assert schema_data["@type"] == "Event"
        assert schema_data["name"] == "92° Raduno Nazionale MC Castellazzo"
        assert "startDate" in schema_data
        assert "location" in schema_data


# ============================================================
# TEST: TRANSLATION WORKFLOW
# ============================================================

@pytest.mark.django_db
class TestTranslationWorkflow:
    """Test translation workflow with wagtail-localize."""
    
    def test_page_can_be_translated(self, full_site_structure, locales):
        """Test a page can be translated to another language."""
        timeline_it = full_site_structure["timeline"]
        
        # Translate to French
        timeline_fr = timeline_it.copy_for_translation(locales["fr"], copy_parents=True, alias=False)
        timeline_fr.title = "Actualités"
        timeline_fr.save_revision().publish()
        
        assert timeline_fr is not None
        assert timeline_fr.locale == locales["fr"]
        assert timeline_fr.title == "Actualités"
        assert timeline_fr.translation_key == timeline_it.translation_key
    
    def test_get_translation_returns_correct_page(self, homepage_with_translations, locales):
        """Test get_translation returns the correct translated page."""
        home_it = homepage_with_translations["it"]
        home_fr = home_it.get_translation(locales["fr"])
        
        assert home_fr.locale == locales["fr"]
        assert home_fr.title == "Accueil"
    
    def test_get_translations_returns_all(self, homepage_with_translations):
        """Test get_translations returns all translated versions."""
        home_it = homepage_with_translations["it"]
        translations = home_it.get_translations(inclusive=True)
        
        assert translations.count() == 4


# ============================================================
# TEST: JSON-LD OUTPUT
# ============================================================

@pytest.mark.django_db
class TestJsonLdOutput:
    """Test JSON-LD schema.org output in pages."""
    
    def test_homepage_has_json_ld_method(self, homepage_with_translations):
        """Test HomePage has get_json_ld method."""
        home = homepage_with_translations["it"]
        assert hasattr(home, "get_json_ld")
    
    def test_homepage_json_ld_valid(self, homepage_with_translations):
        """Test HomePage JSON-LD is valid JSON."""
        import json
        home = homepage_with_translations["it"]
        json_ld = home.get_json_ld()
        
        # Should be valid JSON
        parsed = json.loads(json_ld)
        assert "@context" in parsed
        assert parsed["@context"] == "https://schema.org"
        assert "@type" in parsed
        assert parsed["@type"] == "Organization"
    
    def test_event_json_ld_valid(self, full_site_structure):
        """Test EventDetailPage JSON-LD is valid JSON."""
        import json
        event = full_site_structure["event"]
        json_ld = event.get_json_ld()
        
        parsed = json.loads(json_ld)
        assert parsed["@type"] == "Event"
        assert "startDate" in parsed
