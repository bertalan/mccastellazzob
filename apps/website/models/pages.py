"""
Page models for the website.

mccastellazzob.com - Moto Club Castellazzo Bormida
Modelli pagina che estendono CodeRedCMS con funzionalità custom.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from coderedcms.forms import CoderedFormField
from coderedcms.models import CoderedArticleIndexPage
from coderedcms.models import CoderedArticlePage
from coderedcms.models import CoderedEmail
from coderedcms.models import CoderedEventIndexPage
from coderedcms.models import CoderedEventOccurrence
from coderedcms.models import CoderedEventPage
from coderedcms.models import CoderedFormPage
from coderedcms.models import CoderedLocationIndexPage
from coderedcms.models import CoderedLocationPage
from coderedcms.models import CoderedWebPage
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel

from apps.core.mixins import OpenStreetMapMixin
from apps.core.schema import SchemaOrgEvent
from apps.core.schema import SchemaOrgGenerator
from apps.core.schema import SchemaOrgPlace
from apps.website.blocks import HTML_STREAMBLOCKS
from apps.website.blocks import LAYOUT_STREAMBLOCKS


if TYPE_CHECKING:
    from django.http import HttpRequest


class ArticlePage(CoderedArticlePage):
    """
    Pagina articolo per news e blog.

    Eredita da CoderedArticlePage con template e ordinamento personalizzati.
    """

    class Meta:
        verbose_name = _("Articolo")
        verbose_name_plural = _("Articoli")
        ordering = ["-first_published_at"]

    parent_page_types: ClassVar[list[str]] = ["website.ArticleIndexPage"]
    template = "coderedcms/pages/article_page.html"
    search_template = "coderedcms/pages/article_page.search.html"


class ArticleIndexPage(CoderedArticleIndexPage):
    """
    Pagina indice che mostra la lista degli articoli.
    """

    class Meta:
        verbose_name = _("Pagina indice articoli")

    index_query_pagemodel = "website.ArticlePage"
    subpage_types: ClassVar[list[str]] = ["website.ArticlePage"]
    template = "coderedcms/pages/article_index_page.html"


class EventPage(OpenStreetMapMixin, CoderedEventPage):
    """
    Pagina evento con integrazione OpenStreetMap e JSON-LD.

    Estende CoderedEventPage con:
    - Mappa OSM per la località
    - Generazione automatica JSON-LD schema.org
    - Campo autore personalizzato
    """

    author_display = models.CharField(
        verbose_name=_("Autore visualizzato"),
        max_length=255,
        blank=True,
        help_text=_("Nome autore da visualizzare sull'evento."),
    )

    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventi")

    parent_page_types: ClassVar[list[str]] = ["website.EventIndexPage"]
    template = "coderedcms/pages/event_page.html"

    # Estendiamo i panels base invece di sovrascriverli
    content_panels = CoderedEventPage.content_panels + [
        MultiFieldPanel(
            OpenStreetMapMixin.get_map_panels(),
            heading=_("Mappa OpenStreetMap"),
        ),
        MultiFieldPanel(
            [FieldPanel("author_display")],
            heading=_("Informazioni pubblicazione"),
        ),
    ]

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        """Aggiunge JSON-LD al contesto."""
        context = super().get_context(request)
        context["json_ld_schema"] = self._generate_json_ld()
        return context

    def _generate_json_ld(self) -> str:
        """Genera JSON-LD per l'evento."""
        generator = SchemaOrgGenerator()

        # Ottieni date dall'evento
        start_date = getattr(self, "calendar_start", None) or datetime.now()
        end_date = getattr(self, "calendar_end", None)

        event_data = SchemaOrgEvent(
            name=self.title,
            start_date=start_date,
            end_date=end_date,
            location_name=self.address or self.title,
            address=self.address or "",
            latitude=self.latitude,
            longitude=self.longitude,
            description=self.search_description or "",
            url=self.full_url or "",
        )
        return generator.generate_event(event_data)


class EventIndexPage(CoderedEventIndexPage):
    """
    Pagina indice che mostra la lista degli eventi.
    """

    class Meta:
        verbose_name = _("Pagina indice eventi")

    index_query_pagemodel = "website.EventPage"
    subpage_types: ClassVar[list[str]] = ["website.EventPage"]
    template = "coderedcms/pages/event_index_page.html"


class EventOccurrence(CoderedEventOccurrence):
    """
    Modello per le occorrenze degli eventi (date ricorrenti).

    Richiesto da CodeRedCMS per la gestione del calendario.
    """

    event = ParentalKey(
        "website.EventPage",
        related_name="occurrences",
        on_delete=models.CASCADE,
    )


class LocationPage(OpenStreetMapMixin, CoderedLocationPage):
    """
    Pagina località con integrazione OpenStreetMap e JSON-LD.

    Estende CoderedLocationPage con:
    - Mappa OSM per la località
    - Generazione automatica JSON-LD schema.org/Place
    """

    class Meta:
        verbose_name = _("Località")
        verbose_name_plural = _("Località")

    parent_page_types: ClassVar[list[str]] = ["website.LocationIndexPage"]
    template = "coderedcms/pages/location_page.html"

    # Estendiamo i panels base invece di sovrascriverli
    content_panels = CoderedLocationPage.content_panels + [
        MultiFieldPanel(
            OpenStreetMapMixin.get_map_panels(),
            heading=_("Mappa OpenStreetMap"),
        ),
    ]

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        """Aggiunge JSON-LD al contesto."""
        context = super().get_context(request)
        context["json_ld_schema"] = self._generate_json_ld()
        return context

    def _generate_json_ld(self) -> str:
        """Genera JSON-LD per la località."""
        generator = SchemaOrgGenerator()
        place_data = SchemaOrgPlace(
            name=self.title,
            address=self.address or "",
            latitude=self.latitude,
            longitude=self.longitude,
            description=self.search_description or "",
            url=self.full_url or "",
        )
        return generator.generate_place(place_data)


class LocationIndexPage(CoderedLocationIndexPage):
    """
    Pagina indice che mostra la lista delle località.
    """

    class Meta:
        verbose_name = _("Pagina indice località")

    index_query_pagemodel = "website.LocationPage"
    subpage_types: ClassVar[list[str]] = ["website.LocationPage"]
    template = "coderedcms/pages/location_index_page.html"


class WebPage(CoderedWebPage):
    """
    Pagina web generica con StreamField.

    Usa blocchi HTML e layout filtrati (senza Google Maps).
    """

    class Meta:
        verbose_name = _("Pagina web")
        verbose_name_plural = _("Pagine web")

    template = "coderedcms/pages/web_page.html"

    # Override per usare blocchi filtrati
    body_content_panels = CoderedWebPage.body_content_panels


class FormPage(CoderedFormPage):
    """
    Pagina con form contatti.

    Supporta campi dinamici e email di conferma.
    """

    class Meta:
        verbose_name = _("Pagina form")
        verbose_name_plural = _("Pagine form")

    template = "coderedcms/pages/form_page.html"


class FormPageField(CoderedFormField):
    """
    Campo form per FormPage.
    """

    page = ParentalKey(
        "FormPage",
        related_name="form_fields",
        on_delete=models.CASCADE,
    )


class FormConfirmEmail(CoderedEmail):
    """
    Email di conferma per FormPage.
    """

    page = ParentalKey(
        "FormPage",
        related_name="confirmation_emails",
        on_delete=models.CASCADE,
    )
