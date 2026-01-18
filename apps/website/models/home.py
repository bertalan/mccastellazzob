"""
MC Castellazzo - HomePage Model
================================
schema.org SportsClub/Organization

Usa wagtailseo.SeoSettings come fonte unica per i dati organizzazione.
I campi locali sono solo per contenuti specifici della pagina (hero, CTA).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.core.seo import JsonLdMixin, clean_html, get_organization_data
from apps.website.blocks import (
    HeroSliderBlock,
    HeroCountdownBlock,
    StatsBlock,
    SectionCardsGridBlock,
    CTABlock,
    GalleryBlock,
    ArticleBlock,
)


class HomePage(JsonLdMixin, Page):
    """
    Homepage del sito - schema.org SportsClub/Organization.
    
    I dati organizzazione (nome, indirizzo, telefono, logo) sono gestiti
    centralmente in Settings > SEO (wagtailseo.SeoSettings).
    
    Qui definiamo solo:
    - Contenuti specifici della homepage (hero, CTA)
    - StreamField per componenti visivi
    """
    
    # === HERO SECTION ===
    hero_badge = models.CharField(
        _("Badge hero"),
        max_length=100,
        blank=True,
        help_text=_("Es: IL PIÙ ANTICO MOTO CLUB DEL PIEMONTE"),
    )
    hero_title = models.CharField(
        _("Titolo hero"),
        max_length=255,
        blank=True,
        help_text=_("Es: Moto Club"),
    )
    hero_subtitle = models.CharField(
        _("Sottotitolo hero"),
        max_length=255,
        blank=True,
        help_text=_("Es: Castellazzo Bormida (parte evidenziata in oro)"),
    )
    hero_tagline = models.CharField(
        _("Tagline hero"),
        max_length=500,
        blank=True,
        help_text=_("Es: di passione, adrenalina e fratellanza su due ruote"),
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine hero"),
    )
    
    # Carousel per lo slider fotografico
    hero_carousel = models.ForeignKey(
        "coderedcms.Carousel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Slider fotografico (CodeRedCMS)"),
        help_text=_("Carousel CodeRedCMS - può avere bug, usa Simple Carousel se non funziona."),
    )
    
    # Simple Carousel (alternativa senza bug)
    simple_carousel = models.ForeignKey(
        "website.SimpleCarousel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Simple Carousel"),
        help_text=_("Carousel semplice senza bug - CONSIGLIATO."),
    )
    
    # === CONTENUTO ===
    description = RichTextField(
        _("Descrizione breve"),
        blank=True,
        help_text=_("Breve descrizione del motoclub per la homepage"),
    )
    
    # Evento in evidenza
    featured_event = models.ForeignKey(
        "website.EventDetailPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Evento in evidenza"),
        help_text=_("Evento da mostrare nella homepage"),
    )
    
    # CTA Section
    cta_title = models.CharField(
        _("Titolo CTA"),
        max_length=255,
        blank=True,
        help_text=_("Es: Unisciti a Noi"),
    )
    cta_subtitle = models.CharField(
        _("Sottotitolo CTA"),
        max_length=500,
        blank=True,
        help_text=_("Es: Diventa parte della famiglia del Moto Club più antico del Piemonte"),
    )
    
    # Body StreamField per componenti grafici
    body = StreamField(
        [
            ("hero_slider", HeroSliderBlock()),
            ("hero_countdown", HeroCountdownBlock()),
            ("stats", StatsBlock()),
            ("section_cards", SectionCardsGridBlock()),
            ("cta", CTABlock()),
            ("gallery", GalleryBlock()),
            ("article", ArticleBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Contenuto pagina"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/home_page.jinja2"
    max_count = 1
    
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_badge"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_tagline"),
                FieldPanel("hero_image"),
                FieldPanel("simple_carousel"),
                FieldPanel("hero_carousel"),
            ],
            heading=_("Hero Section"),
        ),
        FieldPanel("description"),
        FieldPanel("featured_event"),
        MultiFieldPanel(
            [
                FieldPanel("cta_title"),
                FieldPanel("cta_subtitle"),
            ],
            heading=_("CTA Section"),
        ),
        FieldPanel("body"),
    ]
    
    class Meta:
        verbose_name = _("Homepage")
        verbose_name_plural = _("Homepage")
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        """Homepage usa SportsClub come tipo principale."""
        return "SportsClub"
    
    def get_json_ld_data(self, request=None) -> dict:
        """
        Dati schema.org SportsClub.
        Prende i dati organizzazione da wagtailseo.SeoSettings.
        Sport e federazione vengono da SiteSettings.
        """
        # Ottieni dati completi da SeoSettings (include sport e memberOf)
        data = get_organization_data(self)
        
        # Aggiungi descrizione dalla pagina se presente
        if self.description:
            data["description"] = clean_html(self.description)
        
        return data
