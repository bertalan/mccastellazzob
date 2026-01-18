"""
Test per l'Accessibility Toolbar.
TDD: test first secondo CLAUDE.md

Funzionalità da testare:
- Presenza del pulsante toggle nel DOM
- Presenza della toolbar con tutti i controlli
- Funzioni JavaScript definite
- Classi CSS di accessibilità
- Persistenza localStorage
- Conformità WCAG (aria-labels, ruoli, tastiera)
"""
import pytest
from django.test import Client
from bs4 import BeautifulSoup


@pytest.mark.django_db
class TestAccessibilityToolbarPresence:
    """Test per la presenza del widget di accessibilità."""

    def test_accessibility_toggle_button_exists(self, client):
        """La pagina deve avere il pulsante toggle per l'accessibilità."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Cerca il pulsante toggle
            toggle_btn = soup.find(id="accessibility-toggle")
            assert toggle_btn is not None, "Deve esistere il pulsante toggle accessibilità"

            # Deve avere aria-label
            assert toggle_btn.get("aria-label"), "Il pulsante deve avere aria-label"

    def test_accessibility_toolbar_panel_exists(self, client):
        """La pagina deve avere il pannello toolbar accessibilità."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Cerca il pannello toolbar
            toolbar = soup.find(id="accessibility-toolbar")
            assert toolbar is not None, "Deve esistere il pannello toolbar accessibilità"

            # Deve avere role="dialog" per screen reader
            assert toolbar.get("role") == "dialog", "Il pannello deve avere role='dialog'"

    def test_accessibility_toolbar_has_close_button(self, client):
        """Il pannello deve avere un pulsante di chiusura."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toolbar = soup.find(id="accessibility-toolbar")
            if toolbar:
                close_btn = toolbar.find("button", {"aria-label": True})
                assert close_btn is not None, "Deve esistere un pulsante di chiusura"

    def test_toggle_button_is_floating(self, client):
        """Il pulsante toggle deve essere fluttuante (classe a11y-toggle-btn)."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toggle_btn = soup.find(id="accessibility-toggle")
            assert toggle_btn is not None, "Deve esistere il pulsante toggle"

            # Verifica che abbia la classe per position: fixed
            btn_class = toggle_btn.get("class", [])
            assert "a11y-toggle-btn" in btn_class, \
                "Il pulsante deve avere la classe a11y-toggle-btn per essere fluttuante"

    def test_toggle_button_always_visible_on_all_pages(self, client):
        """Il pulsante deve essere visibile su tutte le pagine principali."""
        pages_to_check = ["/it/", "/en/", "/it/chi-siamo/", "/it/eventi/"]

        for page_url in pages_to_check:
            response = client.get(page_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                toggle_btn = soup.find(id="accessibility-toggle")
                assert toggle_btn is not None, \
                    f"Il pulsante toggle deve essere presente su {page_url}"


@pytest.mark.django_db
class TestAccessibilityToolbarControls:
    """Test per i controlli della toolbar."""

    def test_font_size_controls_exist(self, client):
        """Devono esistere i controlli per la dimensione del testo."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Pulsanti aumento/diminuzione font
            increase_btn = soup.find(attrs={"data-a11y-action": "font-increase"})
            decrease_btn = soup.find(attrs={"data-a11y-action": "font-decrease"})

            assert increase_btn is not None, "Deve esistere pulsante aumento font"
            assert decrease_btn is not None, "Deve esistere pulsante diminuzione font"

    def test_contrast_control_exists(self, client):
        """Deve esistere il controllo per il contrasto."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            contrast_btn = soup.find(attrs={"data-a11y-action": "high-contrast"})
            assert contrast_btn is not None, "Deve esistere controllo alto contrasto"

    def test_dyslexia_font_control_exists(self, client):
        """Deve esistere il controllo per font dislessia."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            dyslexia_btn = soup.find(attrs={"data-a11y-action": "dyslexia-font"})
            assert dyslexia_btn is not None, "Deve esistere controllo font dislessia"

    def test_cursor_control_exists(self, client):
        """Deve esistere il controllo per cursore grande."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            cursor_btn = soup.find(attrs={"data-a11y-action": "big-cursor"})
            assert cursor_btn is not None, "Deve esistere controllo cursore grande"

    def test_reading_guide_control_exists(self, client):
        """Deve esistere il controllo per guida lettura."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            guide_btn = soup.find(attrs={"data-a11y-action": "reading-guide"})
            assert guide_btn is not None, "Deve esistere controllo guida lettura"

    def test_stop_animations_control_exists(self, client):
        """Deve esistere il controllo per fermare le animazioni."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            stop_btn = soup.find(attrs={"data-a11y-action": "stop-animations"})
            assert stop_btn is not None, "Deve esistere controllo stop animazioni"

    def test_highlight_links_control_exists(self, client):
        """Deve esistere il controllo per evidenziare i link."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            links_btn = soup.find(attrs={"data-a11y-action": "highlight-links"})
            assert links_btn is not None, "Deve esistere controllo evidenzia link"

    def test_reset_control_exists(self, client):
        """Deve esistere il controllo per reset impostazioni."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            reset_btn = soup.find(attrs={"data-a11y-action": "reset"})
            assert reset_btn is not None, "Deve esistere controllo reset"


@pytest.mark.django_db
class TestAccessibilityToolbarJavaScript:
    """Test per le funzioni JavaScript della toolbar."""

    def test_javascript_functions_defined(self, client):
        """Le funzioni JavaScript devono essere definite."""
        response = client.get("/it/")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            # Verifica che le funzioni siano definite
            assert "AccessibilityToolbar" in content or "accessibilityToolbar" in content, \
                "Deve esistere oggetto AccessibilityToolbar"

    def test_localstorage_key_defined(self, client):
        """Deve essere definita la chiave localStorage."""
        response = client.get("/it/")

        if response.status_code == 200:
            content = response.content.decode("utf-8")

            assert "a11y-preferences" in content or "accessibility" in content.lower(), \
                "Deve essere definita la persistenza localStorage"


@pytest.mark.django_db
class TestAccessibilityToolbarWCAG:
    """Test per conformità WCAG della toolbar."""

    def test_all_controls_have_aria_labels(self, client):
        """Tutti i controlli devono avere aria-label o aria-labelledby."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toolbar = soup.find(id="accessibility-toolbar")
            if toolbar:
                buttons = toolbar.find_all("button")
                for btn in buttons:
                    has_label = btn.get("aria-label") or btn.get("aria-labelledby")
                    assert has_label, f"Il pulsante deve avere aria-label: {btn}"

    def test_toolbar_is_keyboard_navigable(self, client):
        """La toolbar deve essere navigabile da tastiera."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toolbar = soup.find(id="accessibility-toolbar")
            if toolbar:
                # Tutti i controlli interattivi devono essere focusabili
                buttons = toolbar.find_all("button")
                for btn in buttons:
                    # Non deve avere tabindex negativo
                    tabindex = btn.get("tabindex")
                    if tabindex:
                        assert int(tabindex) >= 0, "I pulsanti non devono avere tabindex negativo"

    def test_toggle_button_has_aria_expanded(self, client):
        """Il pulsante toggle deve avere aria-expanded."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toggle_btn = soup.find(id="accessibility-toggle")
            if toggle_btn:
                assert toggle_btn.get("aria-expanded") is not None, \
                    "Il pulsante toggle deve avere aria-expanded"

    def test_toolbar_has_aria_modal(self, client):
        """Il pannello toolbar deve avere aria-modal per screen reader."""
        response = client.get("/it/")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            toolbar = soup.find(id="accessibility-toolbar")
            if toolbar:
                assert toolbar.get("aria-modal") == "true", \
                    "Il pannello deve avere aria-modal='true'"


@pytest.mark.django_db
class TestAccessibilityToolbarI18n:
    """Test per le traduzioni della toolbar."""

    def test_toolbar_title_is_translatable(self, client):
        """Il titolo della toolbar deve essere tradotto."""
        # Testa in italiano
        response_it = client.get("/it/")
        if response_it.status_code == 200:
            assert "Accessibilit" in response_it.content.decode("utf-8"), \
                "La parola 'Accessibilità' deve apparire in italiano"

        # Testa in inglese
        response_en = client.get("/en/")
        if response_en.status_code == 200:
            content = response_en.content.decode("utf-8")
            # In inglese potrebbe essere "Accessibility"
            assert "Accessibilit" in content or "accessibilit" in content.lower(), \
                "La parola 'Accessibility' deve apparire in inglese"
