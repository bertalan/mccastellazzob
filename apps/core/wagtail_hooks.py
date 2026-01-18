"""
MC Castellazzo - Wagtail Hooks
==============================
Hooks per aggiungere funzionalità custom al backend Wagtail.
Include il pulsante "Traduci Automaticamente" nel menu azioni delle pagine.
Include il menu "Caricamento Massivo" per le immagini.
"""
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from wagtail.admin.menu import MenuItem


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


@hooks.register("register_admin_urls")
def register_bulk_upload_url():
    """Registra l'URL per il caricamento massivo immagini."""
    from apps.core.admin_views import BulkUploadView
    
    return [
        path(
            "bulk-upload/",
            BulkUploadView.as_view(),
            name="bulk_upload",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_bulk_upload_menu_item():
    """Aggiunge voce menu per caricamento massivo."""
    return MenuItem(
        _("Caricamento Massivo"),
        reverse("bulk_upload"),
        icon_name="image",
        order=350,  # Dopo Immagini (300)
    )


@hooks.register("register_page_action_menu_item")
def register_translate_action():
    """Registra la voce di menu per la traduzione automatica."""
    return TranslateMenuItem()

