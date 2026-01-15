"""
MC Castellazzo - Wagtail Hooks
==============================
Hooks per aggiungere funzionalità custom al backend Wagtail.
Include il pulsante "Traduci Automaticamente" nel menu azioni delle pagine.
"""
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem


class TranslateMenuItem(ActionMenuItem):
    """
    Voce di menu per tradurre automaticamente una pagina.
    Appare solo per pagine non in italiano.
    """
    name = "action-translate"
    label = "🌍 Traduci Automaticamente"
    icon_name = "globe"
    order = 100  # Dopo le azioni standard
    
    def get_url(self, context):
        page = context.get("page")
        if page:
            return reverse("auto_translate_page", args=[page.id])
        return "#"
    
    def is_shown(self, context):
        page = context.get("page")
        if page:
            # Mostra solo per pagine NON in italiano
            return page.locale.language_code != "it"
        return False


@hooks.register("register_admin_urls")
def register_translate_url():
    """Registra l'URL per la traduzione automatica."""
    from apps.core.views import auto_translate_page_view
    
    return [
        path(
            "translate-page/<int:page_id>/",
            auto_translate_page_view,
            name="auto_translate_page",
        ),
    ]


@hooks.register("register_page_action_menu_item")
def register_translate_action():
    """Registra la voce di menu per la traduzione automatica."""
    return TranslateMenuItem()

