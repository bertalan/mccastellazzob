"""
Custom StreamField blocks.

mccastellazzob.com - Moto Club Castellazzo Bormida
Blocchi custom per StreamField, filtrati senza Google Maps.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from coderedcms.blocks import CONTENT_STREAMBLOCKS as CRX_CONTENT_STREAMBLOCKS
from coderedcms.blocks import HTML_STREAMBLOCKS as CRX_HTML_STREAMBLOCKS
from coderedcms.blocks import LAYOUT_STREAMBLOCKS as CRX_LAYOUT_STREAMBLOCKS
from coderedcms.blocks import BaseBlock
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.models import Locale


if TYPE_CHECKING:
    pass


# ==============================================
# BLOCCHI FILTRATI (senza Google Maps)
# ==============================================

# Nomi blocchi Google Maps da escludere
GOOGLE_MAPS_BLOCKS = {"google_map", "googlemaps", "google_maps"}


def filter_google_maps(block_list: list) -> list:
    """
    Filtra i blocchi Google Maps dalla lista.

    Args:
        block_list: Lista di tuple (name, block).

    Returns:
        Lista filtrata senza blocchi Google Maps.
    """
    return [(name, block) for name, block in block_list if name.lower() not in GOOGLE_MAPS_BLOCKS]


# StreamBlocks filtrati per uso nelle pagine
HTML_STREAMBLOCKS = filter_google_maps(list(CRX_HTML_STREAMBLOCKS))
LAYOUT_STREAMBLOCKS = filter_google_maps(list(CRX_LAYOUT_STREAMBLOCKS))
CONTENT_STREAMBLOCKS = filter_google_maps(list(CRX_CONTENT_STREAMBLOCKS))


# ==============================================
# BLOCCHI CUSTOM
# ==============================================


class LatestContentBlock(BaseBlock):
    """
    Blocco per visualizzare gli ultimi contenuti.

    Mostra gli ultimi articoli, eventi o località filtrati per lingua corrente.
    """

    content_type = blocks.ChoiceBlock(
        choices=[
            ("article", _("Articoli")),
            ("event", _("Eventi")),
            ("location", _("Località")),
        ],
        default="article",
        label=_("Tipo contenuto"),
    )

    count = blocks.IntegerBlock(
        default=3,
        min_value=1,
        max_value=12,
        label=_("Numero elementi"),
    )

    title = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("Titolo sezione"),
    )

    class Meta:
        icon = "list-ul"
        label = _("Ultimi contenuti")
        template = "website/blocks/latest_content_block.html"

    def get_context(self, value: dict[str, Any], parent_context: dict | None = None) -> dict:
        """Aggiunge i contenuti filtrati al contesto."""
        context = super().get_context(value, parent_context)

        content_type = value.get("content_type", "article")
        count = value.get("count", 3)

        # Import qui per evitare import circolari
        from apps.website.models.pages import ArticlePage
        from apps.website.models.pages import EventPage
        from apps.website.models.pages import LocationPage

        # Mappa tipo contenuto → modello
        model_map = {
            "article": ArticlePage,
            "event": EventPage,
            "location": LocationPage,
        }

        model = model_map.get(content_type, ArticlePage)

        # Ottieni locale corrente
        try:
            current_locale = Locale.get_active()
            queryset = (
                model.objects.live()
                .filter(locale=current_locale)
                .order_by("-first_published_at")[:count]
            )
        except Exception:
            # Fallback senza filtro locale
            queryset = model.objects.live().order_by("-first_published_at")[:count]

        context["items"] = queryset
        context["title"] = value.get("title", "")

        return context
