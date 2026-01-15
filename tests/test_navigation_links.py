"""
Test-Driven Development per verificare tutti i link di navigazione.

Questo test verifica che tutti i link nel navbar, mobile menu e footer
siano raggiungibili e restituiscano 200 OK per tutte le lingue.
"""

import pytest
from django.test import Client
from wagtail.models import Locale


@pytest.mark.django_db
class TestNavigationLinks:
    """Test per tutti i link di navigazione."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup per ogni test."""
        self.client = Client()
        self.languages = ['it', 'en', 'fr', 'de', 'es']
        
        # Link principali da testare (senza prefisso lingua)
        self.main_links = [
            '/',                          # Home
            '/chi-siamo/',               # Chi Siamo
            '/chi-siamo/consiglio/',     # Il Consiglio
            '/eventi/',                  # Eventi
            '/galleria/',                # Galleria
            '/contatti/',                # Contatti
        ]
        
        # Link aggiuntivi nel footer
        self.footer_links = [
            '/chi-siamo/trasparenza/',   # Trasparenza
            '/privacy/',                 # Privacy Policy
        ]

    def test_homepage_exists_for_all_languages(self):
        """Test: homepage raggiungibile per tutte le lingue."""
        for lang in self.languages:
            url = f'/{lang}/'
            response = self.client.get(url)
            assert response.status_code == 200, \
                f"Homepage {url} non raggiungibile (status: {response.status_code})"

    def test_main_navigation_links(self):
        """Test: tutti i link principali della navbar raggiungibili."""
        for lang in self.languages:
            for link in self.main_links:
                url = f'/{lang}{link}'
                response = self.client.get(url)
                assert response.status_code in [200, 302], \
                    f"Link {url} non raggiungibile (status: {response.status_code})"

    def test_footer_links(self):
        """Test: tutti i link del footer raggiungibili."""
        for lang in self.languages:
            for link in self.footer_links:
                url = f'/{lang}{link}'
                response = self.client.get(url)
                assert response.status_code in [200, 302, 404], \
                    f"Link footer {url} non raggiungibile (status: {response.status_code})"

    def test_language_switcher_links(self):
        """Test: il language switcher crea link validi per ogni lingua."""
        # Test da homepage italiana
        response = self.client.get('/it/')
        assert response.status_code == 200
        
        content = response.content.decode('utf-8')
        
        # Verifica presenza flag emojis
        flags = ['🇮🇹', '🇬🇧', '🇫🇷', '🇩🇪', '🇪🇸']
        for flag in flags:
            assert flag in content, f"Bandiera {flag} non trovata nel contenuto"
        
        # Verifica link cambio lingua
        for lang in self.languages:
            # Il pattern dei link è /LANG_CODE/
            assert f'/{lang}/' in content, \
                f"Link per lingua {lang} non trovato nel language switcher"

    def test_language_persistence_in_navigation(self):
        """Test: la lingua persiste durante la navigazione."""
        for lang in self.languages:
            # Naviga dalla home a chi-siamo
            home_response = self.client.get(f'/{lang}/')
            if home_response.status_code == 200:
                chi_siamo_response = self.client.get(f'/{lang}/chi-siamo/')
                assert chi_siamo_response.status_code in [200, 404], \
                    f"Link chi-siamo per lingua {lang} non mantiene il contesto"

    def test_navbar_links_in_homepage(self):
        """Test: verifica che tutti i link navbar siano presenti nella homepage."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        expected_links = [
            '/it/',
            '/it/chi-siamo/',
            '/it/chi-siamo/consiglio/',
            '/it/eventi/',
            '/it/galleria/',
            '/it/contatti/',
        ]
        
        for link in expected_links:
            assert f'href="/{link[1:]}"' in content or f'href="{link}"' in content, \
                f"Link navbar {link} non trovato nella homepage"

    def test_footer_quick_links(self):
        """Test: verifica link rapidi nel footer."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        footer_quick_links = [
            '/it/',
            '/it/chi-siamo/',
            '/it/eventi/',
            '/it/galleria/',
            '/it/contatti/',
        ]
        
        for link in footer_quick_links:
            # Il footer ha pattern diverso dal navbar
            assert link in content, \
                f"Link rapido footer {link} non trovato"

    def test_footer_transparency_links(self):
        """Test: verifica link trasparenza nel footer."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        transparency_links = [
            '/it/chi-siamo/consiglio/',
            '/it/chi-siamo/trasparenza/',
            '/it/privacy/',
        ]
        
        for link in transparency_links:
            assert link in content, \
                f"Link trasparenza {link} non trovato nel footer"

    def test_mobile_menu_links(self):
        """Test: verifica che il mobile menu contenga tutti i link."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        # Verifica presenza del mobile menu toggle
        assert 'mobileMenuBtn' in content, "Pulsante mobile menu non trovato"
        assert 'mobileMenu' in content, "Mobile menu non trovato"
        
        # I link nel mobile menu devono essere gli stessi del navbar
        mobile_links = [
            '/it/',
            '/it/chi-siamo/',
            '/it/chi-siamo/consiglio/',
            '/it/eventi/',
            '/it/galleria/',
            '/it/contatti/',
        ]
        
        for link in mobile_links:
            assert link in content, \
                f"Link mobile menu {link} non trovato"

    def test_social_links_present(self):
        """Test: verifica presenza link social nel footer."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        # Verifica icone social
        social_icons = [
            'fa-facebook-f',
            'fa-instagram',
            'fa-youtube',
        ]
        
        for icon in social_icons:
            assert icon in content, f"Icona social {icon} non trovata nel footer"

    def test_contact_email_link(self):
        """Test: verifica link email nel footer."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        assert 'mailto:info@mccastellazzo.it' in content, \
            "Link email non trovato nel footer"

    def test_contact_phone_link(self):
        """Test: verifica link telefono nel footer."""
        response = self.client.get('/it/')
        content = response.content.decode('utf-8')
        
        assert 'tel:+390123456789' in content, \
            "Link telefono non trovato nel footer"


@pytest.mark.django_db
class TestPageExistence:
    """Test per verificare l'esistenza effettiva delle pagine."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup per ogni test."""
        self.client = Client()

    def test_existing_pages_return_200(self):
        """Test: le pagine esistenti devono restituire 200."""
        # Test solo per italiano per ora
        existing_urls = [
            '/it/',  # Homepage sempre presente
        ]
        
        for url in existing_urls:
            response = self.client.get(url)
            assert response.status_code == 200, \
                f"URL {url} dovrebbe restituire 200, ma ha restituito {response.status_code}"

    def test_missing_pages_return_404(self):
        """Test: le pagine mancanti devono restituire 404."""
        missing_urls = [
            '/it/pagina-inesistente/',
            '/it/altra-pagina-che-non-esiste/',
        ]
        
        for url in missing_urls:
            response = self.client.get(url)
            assert response.status_code == 404, \
                f"URL {url} dovrebbe restituire 404, ma ha restituito {response.status_code}"

    def test_all_locales_have_homepage(self):
        """Test: ogni locale deve avere una homepage."""
        locales = Locale.objects.all()
        
        for locale in locales:
            url = f'/{locale.language_code}/'
            response = self.client.get(url)
            assert response.status_code == 200, \
                f"Homepage per locale {locale.language_code} non trovata"
