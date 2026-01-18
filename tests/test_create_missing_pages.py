"""
Test TDD per creare le pagine mancanti.

RED PHASE: Questi test falliranno fino a quando le pagine non saranno create.
GREEN PHASE: Creiamo le pagine e i test passano.
"""

import pytest
from django.test import Client
from wagtail.models import Locale, Page
from apps.website.models import HomePage


@pytest.mark.django_db
class TestMissingPages:
    """Test per verificare l'esistenza delle pagine mancanti."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup per ogni test."""
        self.client = Client()
        self.locale_it = Locale.objects.get(language_code='it')

    def test_consiglio_page_exists(self):
        """Test: la pagina Il Consiglio deve esistere."""
        response = self.client.get('/it/chi-siamo/consiglio/')
        assert response.status_code == 200, \
            f"Pagina Il Consiglio non trovata (status: {response.status_code})"

    def test_galleria_page_exists(self):
        """Test: la pagina Galleria deve esistere."""
        response = self.client.get('/it/galleria/')
        assert response.status_code == 200, \
            f"Pagina Galleria non trovata (status: {response.status_code})"

    def test_contatti_page_exists(self):
        """Test: la pagina Contatti deve esistere."""
        response = self.client.get('/it/chi-siamo/contatti/')
        assert response.status_code == 200, \
            f"Pagina Contatti non trovata (status: {response.status_code})"

    def test_privacy_page_exists(self):
        """Test: la pagina Privacy deve esistere."""
        response = self.client.get('/it/privacy/')
        assert response.status_code == 200, \
            f"Pagina Privacy non trovata (status: {response.status_code})"

    def test_consiglio_page_has_content(self):
        """Test: la pagina Il Consiglio deve avere contenuto."""
        response = self.client.get('/it/chi-siamo/consiglio/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            # Verifica presenza di contenuto specifico del consiglio
            assert 'Consiglio' in content or 'Direttivo' in content, \
                "Pagina Il Consiglio non contiene il contenuto atteso"

    def test_galleria_page_has_content(self):
        """Test: la pagina Galleria deve avere contenuto."""
        response = self.client.get('/it/galleria/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            assert 'Galleria' in content or 'foto' in content.lower(), \
                "Pagina Galleria non contiene il contenuto atteso"

    def test_contatti_page_has_form(self):
        """Test: la pagina Contatti deve avere un form o informazioni di contatto."""
        response = self.client.get('/it/chi-siamo/contatti/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            has_form = '<form' in content
            has_email = 'mail' in content.lower()
            has_phone = 'tel' in content.lower() or 'telefono' in content.lower()
            
            assert has_form or has_email or has_phone, \
                "Pagina Contatti non contiene form o informazioni di contatto"

    def test_all_pages_have_correct_language(self):
        """Test: tutte le pagine devono essere in italiano."""
        urls = [
            '/it/chi-siamo/consiglio/',
            '/it/galleria/',
            '/it/chi-siamo/contatti/',
            '/it/privacy/',
        ]
        
        for url in urls:
            response = self.client.get(url)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                assert 'lang="it"' in content or 'lang=\'it\'' in content, \
                    f"Pagina {url} non ha lang='it' impostato"


@pytest.mark.django_db
class TestPagesInWagtailTree:
    """Test per verificare che le pagine siano nella struttura Wagtail."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup per ogni test."""
        self.locale_it = Locale.objects.get(language_code='it')

    def test_consiglio_page_in_tree(self):
        """Test: Il Consiglio deve essere nel tree sotto Chi Siamo."""
        # Cerchiamo la pagina Chi Siamo
        chi_siamo = Page.objects.filter(
            slug='chi-siamo',
            locale=self.locale_it
        ).first()
        
        if chi_siamo:
            # Cerchiamo Consiglio come child
            consiglio = Page.objects.filter(
                slug='consiglio',
                locale=self.locale_it
            ).descendant_of(chi_siamo).first()
            
            assert consiglio is not None, \
                "Pagina Consiglio non trovata nel tree sotto Chi Siamo"
            assert consiglio.live, \
                "Pagina Consiglio non è pubblicata"

    def test_galleria_page_in_tree(self):
        """Test: Galleria deve essere nel tree sotto homepage."""
        home = HomePage.objects.filter(locale=self.locale_it).first()
        
        if home:
            galleria = Page.objects.filter(
                slug='galleria',
                locale=self.locale_it
            ).descendant_of(home).first()
            
            assert galleria is not None, \
                "Pagina Galleria non trovata nel tree sotto homepage"
            assert galleria.live, \
                "Pagina Galleria non è pubblicata"

    def test_contatti_page_in_tree(self):
        """Test: Contatti deve essere nel tree sotto homepage."""
        home = HomePage.objects.filter(locale=self.locale_it).first()
        
        if home:
            contatti = Page.objects.filter(
                slug='contatti',
                locale=self.locale_it
            ).descendant_of(home).first()
            
            assert contatti is not None, \
                "Pagina Contatti non trovata nel tree sotto homepage"
            assert contatti.live, \
                "Pagina Contatti non è pubblicata"

    def test_privacy_page_in_tree(self):
        """Test: Privacy deve essere nel tree sotto homepage."""
        home = HomePage.objects.filter(locale=self.locale_it).first()
        
        if home:
            privacy = Page.objects.filter(
                slug='privacy',
                locale=self.locale_it
            ).descendant_of(home).first()
            
            assert privacy is not None, \
                "Pagina Privacy non trovata nel tree sotto homepage"
            assert privacy.live, \
                "Pagina Privacy non è pubblicata"
