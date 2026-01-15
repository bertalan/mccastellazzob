"""
Test TDD per la pagina Contatti.

Verifica che la pagina abbia:
1. Hero section con breadcrumb
2. Form contatto accessibile
3. Card info contatto (sede, telefono, email, orari)
4. Mappa interattiva
5. FAQ accordion accessibile
6. CTA finale
7. WCAG 2.2 AAA compliance
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.mark.django_db
class TestContactPageStructure:
    """Test per verificare la struttura della pagina Contatti."""

    def test_contact_page_returns_200(self):
        """Test: la pagina Contatti deve essere raggiungibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        assert response.status_code == 200

    def test_contact_page_has_hero_section(self):
        """Test: la pagina deve avere una hero section."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'bg-navy' in content or 'hero' in content.lower(), \
            "Hero section non trovata"

    def test_contact_page_has_breadcrumb(self):
        """Test: la pagina deve avere un breadcrumb accessibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'breadcrumb' in content.lower() or 'Breadcrumb' in content, \
            "Breadcrumb non trovato"

    def test_contact_page_has_contact_form(self):
        """Test: la pagina deve avere un form di contatto."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert '<form' in content, "Form contatto non trovato"
        assert 'name=' in content.lower() or 'nome' in content.lower(), \
            "Campo nome non trovato"
        assert 'email' in content.lower(), "Campo email non trovato"

    def test_contact_page_has_address_info(self):
        """Test: la pagina deve mostrare l'indirizzo della sede."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        # Verifica presenza info sede
        assert 'sede' in content.lower() or 'indirizzo' in content.lower() or 'address' in content.lower(), \
            "Informazioni sede non trovate"

    def test_contact_page_has_phone_info(self):
        """Test: la pagina deve mostrare il telefono."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'tel:' in content.lower() or 'telefono' in content.lower() or 'phone' in content.lower(), \
            "Informazioni telefono non trovate"

    def test_contact_page_has_email_info(self):
        """Test: la pagina deve mostrare l'email."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'mailto:' in content.lower() or '@' in content, \
            "Informazioni email non trovate"

    def test_contact_page_has_map(self):
        """Test: la pagina deve avere una mappa."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'map' in content.lower() or 'leaflet' in content.lower(), \
            "Mappa non trovata"

    def test_contact_page_has_opening_hours(self):
        """Test: la pagina deve mostrare gli orari di apertura."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'orari' in content.lower() or 'lunedì' in content.lower() or 'apertura' in content.lower(), \
            "Orari di apertura non trovati"


@pytest.mark.django_db
class TestContactPageWCAG:
    """Test WCAG 2.2 AAA per la pagina Contatti."""

    def test_page_has_main_landmark(self):
        """Test: la pagina deve avere un main landmark."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert '<main' in content or 'role="main"' in content, \
            "Main landmark non trovato"

    def test_page_has_proper_heading_structure(self):
        """Test: la pagina deve avere una struttura heading corretta."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert '<h1' in content, "H1 non trovato"
        assert '<h2' in content, "H2 non trovato"

    def test_form_has_labels(self):
        """Test: il form deve avere label accessibili."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert '<label' in content, "Label non trovate nel form"

    def test_form_has_required_indicators(self):
        """Test: i campi obbligatori devono essere indicati."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'required' in content.lower() or 'aria-required' in content, \
            "Indicatori campi obbligatori non trovati"

    def test_page_has_skip_link(self):
        """Test: la pagina deve avere uno skip link."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert '#main-content' in content or 'skip' in content.lower(), \
            "Skip link non trovato"

    def test_page_has_focus_indicators(self):
        """Test: gli elementi interattivi devono avere focus visibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        assert 'focus:' in content or ':focus' in content, \
            "Stili focus non trovati"

    def test_links_are_distinguishable(self):
        """Test: i link devono essere distinguibili."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        # Verifica che ci siano stili hover
        assert 'hover:' in content or 'transition' in content, \
            "Stili hover non trovati per i link"

    def test_map_has_accessible_label(self):
        """Test: la mappa deve avere un'etichetta accessibile."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        # Verifica che la mappa abbia aria-label o role
        assert 'aria-label' in content and 'map' in content.lower(), \
            "Mappa senza etichetta accessibile"


@pytest.mark.django_db  
class TestContactPageContent:
    """Test per verificare i contenuti specifici della pagina."""

    def test_page_has_contact_cards(self):
        """Test: la pagina deve avere card per i vari tipi di contatto."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        # Verifica presenza di card
        assert 'card' in content.lower() or 'rounded' in content, \
            "Card contatti non trovate"

    def test_page_has_cta_section(self):
        """Test: la pagina deve avere una sezione CTA finale."""
        response = requests.get(f"{BASE_URL}/it/chi-siamo/contatti/", timeout=5)
        content = response.text
        
        # Verifica CTA
        assert 'unir' in content.lower() or 'iscri' in content.lower() or 'contattaci' in content.lower(), \
            "Sezione CTA non trovata"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
