"""
MC Castellazzo - Events Pages Models
=====================================
Pagine Eventi con:
- EventsPage (schema.org EventSeries - eventi anno corrente)
- EventDetailPage (schema.org Event - dettaglio singolo evento)
- EventsArchivePage (archivio storico per anno)

I dati organizzatore (Organizer) vengono da wagtailseo.SeoSettings.
"""
from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.core.seo import JsonLdMixin, clean_html, get_organization_data, event as schema_event, place
from apps.website.blocks import GalleryImageBlock, HeroCountdownBlock
from wagtail.search import index


class EventPageTag(TaggedItemBase):
    """
    Tag per gli eventi - usa taggit standard per condividere
    gli stessi Tag con tutto il sito (articoli, gallerie, ecc.)
    """
    content_object = ParentalKey(
        "website.EventDetailPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class EventDetailPage(JsonLdMixin, Page):
    """
    Pagina dettaglio evento singolo - schema.org Event.
    """
    
    # Campi Event
    event_name = models.CharField(
        _("Nome evento"),
        max_length=255,
    )
    
    start_date = models.DateTimeField(
        _("Data inizio"),
    )
    
    end_date = models.DateTimeField(
        _("Data fine"),
        null=True,
        blank=True,
    )
    
    # Location (Place)
    location_name = models.CharField(
        _("Nome luogo"),
        max_length=255,
    )
    
    location_address = models.CharField(
        _("Indirizzo luogo"),
        max_length=500,
        blank=True,
    )
    
    location_lat = models.FloatField(
        _("Latitudine"),
        null=True,
        blank=True,
    )
    
    location_lon = models.FloatField(
        _("Longitudine"),
        null=True,
        blank=True,
    )
    
    # Dettagli
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine"),
    )
    
    description = RichTextField(
        _("Descrizione"),
        blank=True,
    )
    
    event_status = models.CharField(
        _("Stato evento"),
        max_length=20,
        choices=[
            ("EventScheduled", _("Programmato")),
            ("EventCancelled", _("Annullato")),
            ("EventPostponed", _("Posticipato")),
            ("EventRescheduled", _("Riprogrammato")),
        ],
        default="EventScheduled",
    )
    
    # Galleria (StreamField invece di ManyToManyField per compatibilità Wagtail)
    gallery = StreamField(
        [
            ("image", GalleryImageBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Galleria immagini"),
    )
    
    # Tags - usa lo stesso sistema di CodeRedCMS per condividere i tag
    tags = ClusterTaggableManager(
        through="website.EventPageTag",
        blank=True,
        verbose_name=_("Tag"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/event_detail_page.jinja2"
    parent_page_types = ["website.EventsPage", "website.EventsArchivePage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("event_name"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("event_status"),
            ],
            heading=_("Date e Stato"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("location_name"),
                FieldPanel("location_address"),
                FieldPanel("location_lat"),
                FieldPanel("location_lon"),
            ],
            heading=_("Luogo"),
        ),
        FieldPanel("image"),
        FieldPanel("description"),
        FieldPanel("gallery"),
        FieldPanel("tags"),
    ]
    
    # Campi indicizzati per la ricerca
    search_fields = Page.search_fields + [
        index.SearchField("event_name", boost=2),
        index.SearchField("location_name", boost=1.5),
        index.SearchField("location_address"),
        index.SearchField("description"),
        index.RelatedFields("tags", [index.SearchField("name")]),
        index.AutocompleteField("event_name"),
        index.AutocompleteField("location_name"),
    ]
    
    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventi")
    
    def __str__(self):
        return self.event_name or self.title
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "Event"
    
    def get_json_ld_data(self, request=None) -> dict:
        
        location = place(
            name=self.location_name,
            street=self.location_address,
            lat=self.location_lat,
            lon=self.location_lon,
        )
        
        data = schema_event(
            name=self.event_name,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat() if self.end_date else "",
            location=location,
            image_url=self.image.get_rendition("original").url if self.image else "",
            description=clean_html(self.description),
            event_status=self.event_status,
            url=self.full_url,
        )
        
        # Aggiungi organizer da SeoSettings (fonte unica)
        data["organizer"] = get_organization_data(self)
        
        return data


class EventsPage(JsonLdMixin, Page):
    """
    Pagina lista eventi anno corrente - schema.org EventSeries.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    # Hero section con countdown
    hero = StreamField(
        [
            ("hero_countdown", HeroCountdownBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Hero Section"),
    )
    
    # Evento in evidenza
    featured_event = models.ForeignKey(
        "website.EventDetailPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Evento in evidenza"),
        help_text=_("Evento da mostrare in primo piano con countdown"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/events_page.jinja2"
    subpage_types = ["website.EventDetailPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("hero"),
        FieldPanel("featured_event"),
    ]
    
    class Meta:
        verbose_name = _("Eventi")
        verbose_name_plural = _("Eventi")
    
    def get_current_year_events(self):
        """
        Ritorna gli eventi dell'anno corrente, ordinati per data.
        """
        current_year = date.today().year
        return (
            EventDetailPage.objects
            .child_of(self)
            .live()
            .filter(start_date__year=current_year)
            .order_by("start_date")
        )
    
    def get_upcoming_events(self):
        """
        Ritorna gli eventi futuri (da oggi in poi).
        """
        today = date.today()
        return (
            EventDetailPage.objects
            .child_of(self)
            .live()
            .filter(start_date__gte=today)
            .order_by("start_date")
        )
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "EventSeries"
    
    def get_json_ld_data(self, request=None) -> dict:
        events = self.get_current_year_events()
        sub_events = []
        
        for evt in events:
            sub_events.append({
                "@type": "Event",
                "name": evt.event_name,
                "startDate": evt.start_date.isoformat(),
                "url": evt.full_url,
            })
        
        return {
            "name": self.title,
            "description": clean_html(self.intro),
            "subEvent": sub_events,
        }


class EventsArchivePage(JsonLdMixin, Page):
    """
    Pagina archivio storico eventi - raggruppa per anno.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    # === Wagtail Config ===
    template = "website/pages/events_archive_page.jinja2"
    subpage_types = ["website.EventDetailPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]
    
    class Meta:
        verbose_name = _("Archivio Eventi")
        verbose_name_plural = _("Archivio Eventi")
    
    def get_events_by_year(self):
        """
        Ritorna gli eventi passati raggruppati per anno (anno più recente in cima).
        """
        today = date.today()
        events = (
            EventDetailPage.objects
            .child_of(self)
            .live()
            .filter(start_date__lt=today)
            .order_by("-start_date")
        )
        
        # Raggruppa per anno
        by_year = {}
        for evt in events:
            year = evt.start_date.year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(evt)
        
        # Ordina per anno decrescente
        return sorted(by_year.items(), key=lambda x: x[0], reverse=True)
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "ItemList"
    
    def get_json_ld_data(self, request=None) -> dict:
        items = []
        position = 1
        
        for year, events in self.get_events_by_year():
            for evt in events:
                items.append({
                    "@type": "ListItem",
                    "position": position,
                    "item": {
                        "@type": "Event",
                        "name": evt.event_name,
                        "startDate": evt.start_date.isoformat(),
                        "url": evt.full_url,
                    },
                })
                position += 1
        
        return {
            "name": self.title,
            "description": clean_html(self.intro),
            "numberOfItems": len(items),
            "itemListElement": items,
        }
