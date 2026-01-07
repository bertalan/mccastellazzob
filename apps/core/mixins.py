"""
Mixin condivisi per i modelli.

mccastellazzob.com - Moto Club Castellazzo Bormida
Contiene mixin riutilizzabili per funzionalità comuni.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtailgeowidget import geocoders
from wagtailgeowidget.panels import LeafletPanel


if TYPE_CHECKING:
    from wagtail.admin.panels import Panel


class OpenStreetMapMixin(models.Model):
    """
    Mixin per aggiungere supporto mappe OpenStreetMap a un modello.

    Fornisce:
    - Campo indirizzo testuale
    - Campo coordinate GPS (latitudine, longitudine)
    - Pannelli Wagtail pre-configurati per l'admin
    - Metodi helper per accedere a lat/lng separatamente

    Utilizzo:
        class MyPage(OpenStreetMapMixin, Page):
            content_panels = Page.content_panels + OpenStreetMapMixin.get_map_panels()
    """

    address = models.CharField(
        verbose_name=_("Indirizzo"),
        max_length=500,
        blank=True,
        help_text=_("Indirizzo della località per la visualizzazione sulla mappa."),
    )

    location = models.CharField(
        verbose_name=_("Coordinate GPS"),
        max_length=250,
        blank=True,
        help_text=_("Coordinate nel formato 'latitudine,longitudine'. Clicca sulla mappa."),
    )

    zoom = models.SmallIntegerField(
        verbose_name=_("Livello zoom"),
        blank=True,
        null=True,
        default=14,
        help_text=_("Livello di zoom della mappa (1-18)."),
    )

    class Meta:
        abstract = True

    @property
    def latitude(self) -> float | None:
        """Restituisce la latitudine come float."""
        if self.location and "," in self.location:
            try:
                return float(self.location.split(",")[0].strip())
            except (ValueError, IndexError):
                return None
        return None

    @property
    def longitude(self) -> float | None:
        """Restituisce la longitudine come float."""
        if self.location and "," in self.location:
            try:
                return float(self.location.split(",")[1].strip())
            except (ValueError, IndexError):
                return None
        return None

    @property
    def has_valid_location(self) -> bool:
        """Verifica se le coordinate sono valide."""
        return self.latitude is not None and self.longitude is not None

    @classmethod
    def get_map_panels(cls) -> list[Panel]:
        """Restituisce i pannelli Wagtail per la gestione della mappa."""
        return [
            FieldPanel("address"),
            FieldPanel("zoom"),
            LeafletPanel(
                "location",
                address_field="address",
            ),
        ]
