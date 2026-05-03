"""
MC Castellazzo - Wagtail Hooks
==============================
Hooks per aggiungere funzionalità custom al backend Wagtail.
Include il pulsante "Traduci Automaticamente" nel menu azioni delle pagine.
Include il menu "Caricamento Massivo" per le immagini.
Include lo script di geocoding automatico per gli indirizzi.
"""
from django.urls import path, reverse
from django.utils.html import format_html
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
    from apps.core.admin_views import BulkUploadView, get_image_metadata
    
    return [
        path(
            "bulk-upload/",
            BulkUploadView.as_view(),
            name="bulk_upload",
        ),
        path(
            "api/image-metadata/<int:image_id>/",
            get_image_metadata,
            name="image_metadata_api",
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


@hooks.register("insert_global_admin_js")
def global_admin_js():
    """Aggiunge script custom per l'admin Wagtail."""
    return format_html(
        '<script src="{}"></script>'
        '<script src="{}"></script>',
        "/static/js/address_geocoding.js",
        "/static/js/gallery_image_metadata.js"
    )


# ---------------------------------------------------------------------------
# Traduzione in background al primo caricamento di una pagina tradotta
# ---------------------------------------------------------------------------
import threading

# Tiene traccia delle (locale_code) già avviate in questa sessione del processo
# per non spammare thread ad ogni visita
_bg_translate_started: set = set()
_bg_translate_lock = threading.Lock()


@hooks.register("before_serve_page")
def trigger_background_translation(page, request, serve_args, serve_kwargs):
    """
    Quando una pagina viene servita in una lingua diversa dall'italiano,
    controlla se ci sono stringhe pendenti e avvia la traduzione in background.

    Il thread parte al massimo UNA volta per lingua per ciclo di vita del
    worker Gunicorn (evita avvii ripetuti ad ogni richiesta).
    Usa il lock globale di translate_pending_segments: se è già in corso,
    il nuovo thread esce subito.
    """
    locale_code = page.locale.language_code
    if locale_code == "it":
        return  # Niente da fare per la lingua sorgente

    with _bg_translate_lock:
        if locale_code in _bg_translate_started:
            return  # Questo worker ha già avviato un thread per questa lingua
        _bg_translate_started.add(locale_code)

    def _run():
        try:
            import django
            from apps.core.machine_translator import translate_pending_segments
            translate_pending_segments(locale_code=locale_code)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error(
                f"Background translation [{locale_code}] errore: {exc}"
            )
        finally:
            # Rimuovi dal set per permettere un nuovo ciclo dopo il completamento
            with _bg_translate_lock:
                _bg_translate_started.discard(locale_code)

    t = threading.Thread(target=_run, daemon=True, name=f"bg-translate-{locale_code}")
    t.start()

