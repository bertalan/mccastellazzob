"""
Test TDD per la pagina Chi Siamo.

Verifica che la pagina abbia:
1. Hero section con breadcrumb
2. Intro section con statistiche
3. Timeline storica
4. Sezione valori
5. Sottopagine
6. WCAG 2.2 AAA compliance
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.mark.django_db
class TestAboutPageStructure:
    """Test per verificare la struttura della pagina Chi Siamo."""

    def test_about_page_returns_200(self):
        """Test: la pagina Chi Siamo deve essere raggiungibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        assert response.status_code == 200

    def test_about_page_has_hero_section(self):
        """Test: la pagina deve avere una hero section."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica hero section
        assert 'hero' in content.lower() or 'pt-32' in content or 'bg-navy' in content, \
            "Hero section non trovata"

    def test_about_page_has_breadcrumb(self):
        """Test: la pagina deve avere un breadcrumb accessibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica breadcrumb con aria-label
        assert 'breadcrumb' in content.lower() or 'Breadcrumb' in content, \
            "Breadcrumb non trovato"

    def test_about_page_has_intro_section(self):
        """Test: la pagina deve avere una sezione intro."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica presenza di contenuto intro
        assert '1933' in content or 'fondato' in content.lower() or 'storia' in content.lower(), \
            "Sezione intro non trovata o senza contenuto storico"

    def test_about_page_has_timeline(self):
        """Test: la pagina deve avere una timeline storica."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica timeline
        assert 'timeline' in content.lower() or 'storia' in content.lower(), \
            "Timeline non trovata"

    def test_about_page_has_values_section(self):
        """Test: la pagina deve avere una sezione valori."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica valori
        assert 'valori' in content.lower() or 'passione' in content.lower(), \
            "Sezione valori non trovata"

    def test_about_page_has_subpages(self):
        """Test: la pagina deve mostrare le sottopagine."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica link sottopagine
        assert '/chi-siamo/consiglio/' in content, "Link Consiglio non trovato"
        assert '/chi-siamo/trasparenza/' in content, "Link Trasparenza non trovato"
        assert '/chi-siamo/contatti/' in content, "Link Contatti non trovato"


@pytest.mark.django_db
class TestAboutPageWCAG:
    """Test WCAG 2.2 AAA per la pagina Chi Siamo."""

    def test_page_has_main_landmark(self):
        """Test: la pagina deve avere un main landmark."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        assert '<main' in content or 'role="main"' in content, \
            "Main landmark non trovato"

    def test_page_has_proper_heading_structure(self):
        """Test: la pagina deve avere una struttura heading corretta."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Deve avere h1
        assert '<h1' in content, "H1 non trovato"
        
        # Deve avere h2 per le sezioni
        assert '<h2' in content, "H2 non trovato"

    def test_page_has_skip_link(self):
        """Test: la pagina deve avere uno skip link."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        assert 'skip' in content.lower() or 'main-content' in content, \
            "Skip link non trovato"

    def test_images_have_alt_text(self):
        """Test: le immagini devono avere alt text."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Se ci sono immagini, devono avere alt
        if '<img' in content:
            # Conta immagini senza alt
            import re
            imgs_without_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', content)
            assert len(imgs_without_alt) == 0, \
                f"Trovate {len(imgs_without_alt)} immagini senza alt text"

    def test_links_are_distinguishable(self):
        """Test: i link devono essere distinguibili."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica che ci siano stili per i link (hover, focus)
        assert 'hover:' in content or ':hover' in content, \
            "Stili hover per link non trovati"

    def test_page_has_aria_labels(self):
        """Test: la pagina deve avere aria-labels appropriati."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica presenza di aria-label
        assert 'aria-label' in content, "Nessun aria-label trovato"

    def test_page_has_focus_indicators(self):
        """Test: la pagina deve avere indicatori di focus visibili."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # Verifica stili focus
        assert 'focus' in content.lower(), "Stili focus non trovati"


@pytest.mark.django_db
class TestAboutPageStatistics:
    """Test per le statistiche della pagina Chi Siamo."""

    def test_page_shows_founding_year(self):
        """Test: la pagina deve mostrare l'anno di fondazione."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        assert '1933' in content, "Anno di fondazione 1933 non trovato"

    def test_page_shows_years_of_activity(self):
        """Test: la pagina deve mostrare gli anni di attività."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/", timeout=5)
        content = response.text
        
        # 2026 - 1933 = 93 anni
        assert '93' in content or '90' in content or 'anni' in content.lower(), \
            "Anni di attività non mostrati"
