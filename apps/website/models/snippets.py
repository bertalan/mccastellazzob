"""
Snippet models for the website.

mccastellazzob.com - Moto Club Castellazzo Bormida
Snippet multilingua per navbar e footer.
"""

from __future__ import annotations

from typing import ClassVar

from coderedcms.blocks import BaseLinkBlock, LinkStructValue
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, TranslatableMixin
from wagtail.snippets.models import register_snippet


class NavbarLinkBlock(BaseLinkBlock):
    """
    Blocco per link singolo nella navbar.
    Eredita da CodeRedCMS BaseLinkBlock per gestione automatica dei link.
    """

    icon = blocks.CharBlock(
        label=_("Icona FontAwesome"),
        max_length=50,
        required=False,
        help_text=_("Es: fas fa-home"),
    )

    class Meta:
        label = _("Link")
        icon = "link"
        value_class = LinkStructValue


class NavbarDropdownBlock(blocks.StructBlock):
    """
    Blocco per dropdown nella navbar con link multipli.
    """

    title = blocks.CharBlock(
        label=_("Titolo dropdown"),
        max_length=255,
    )
    icon = blocks.CharBlock(
        label=_("Icona FontAwesome"),
        max_length=50,
        required=False,
        help_text=_("Es: fas fa-info-circle"),
    )
    links = blocks.ListBlock(
        NavbarLinkBlock(),
        label=_("Link nel dropdown"),
    )

    class Meta:
        label = _("Dropdown")
        icon = "list-ul"


class FooterColumnBlock(blocks.StructBlock):
    """
    Blocco per colonna del footer.
    """

    title = blocks.CharBlock(
        label=_("Titolo colonna"),
        max_length=255,
    )
    links = blocks.ListBlock(
        NavbarLinkBlock(),
        label=_("Link"),
    )

    class Meta:
        label = _("Colonna Footer")
        icon = "list-ul"


class SocialLinkBlock(blocks.StructBlock):
    """
    Blocco per link social.
    """

    platform = blocks.ChoiceBlock(
        label=_("Piattaforma"),
        choices=[
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("youtube", "YouTube"),
            ("twitter", "Twitter/X"),
            ("whatsapp", "WhatsApp"),
        ],
    )
    url = blocks.URLBlock(
        label=_("URL"),
    )

    class Meta:
        label = _("Social Link")
        icon = "site"


@register_snippet
class Navbar(TranslatableMixin, models.Model):
    """
    Navbar multilingua.

    Snippet con TranslatableMixin per supporto IT/EN/DE/FR/ES.
    Ogni lingua ha la propria versione della navbar.
    """

    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=255,
        help_text=_("Nome identificativo della navbar (es. 'Main Navigation')."),
    )

    is_active = models.BooleanField(
        verbose_name=_("Attiva"),
        default=True,
        help_text=_("Solo la navbar attiva verrà mostrata."),
    )

    menu_items = StreamField(
        [
            ("link", NavbarLinkBlock()),
            ("dropdown", NavbarDropdownBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Voci di menu"),
    )

    panels: ClassVar[list] = [
        FieldPanel("name"),
        FieldPanel("is_active"),
        FieldPanel("menu_items"),
    ]

    class Meta:
        verbose_name = _("Navbar")
        verbose_name_plural = _("Navbar")
        unique_together = [("translation_key", "locale")]

    def __str__(self) -> str:
        return f"{self.name} ({self.locale})"


@register_snippet
class Footer(TranslatableMixin, models.Model):
    """
    Footer multilingua.

    Snippet con TranslatableMixin per supporto IT/EN/DE/FR/ES.
    Ogni lingua ha la propria versione del footer.
    """

    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=255,
        help_text=_("Nome identificativo del footer."),
    )

    is_active = models.BooleanField(
        verbose_name=_("Attivo"),
        default=True,
        help_text=_("Solo il footer attivo verrà mostrato."),
    )

    tagline = models.CharField(
        verbose_name=_("Tagline"),
        max_length=500,
        blank=True,
        help_text=_("Breve descrizione sotto il logo."),
    )

    columns = StreamField(
        [
            ("column", FooterColumnBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Colonne link"),
    )

    social_links = StreamField(
        [
            ("social", SocialLinkBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Link social"),
    )

    copyright_text = models.CharField(
        verbose_name=_("Testo copyright"),
        max_length=255,
        blank=True,
        help_text=_("Es: © 2026 MC Castellazzo. Tutti i diritti riservati."),
    )

    panels: ClassVar[list] = [
        FieldPanel("name"),
        FieldPanel("is_active"),
        FieldPanel("tagline"),
        FieldPanel("columns"),
        FieldPanel("social_links"),
        FieldPanel("copyright_text"),
    ]

    class Meta:
        verbose_name = _("Footer")
        verbose_name_plural = _("Footer")
        unique_together = [("translation_key", "locale")]

    def __str__(self) -> str:
        return f"{self.name} ({self.locale})"


@register_snippet
class GalleryCategory(TranslatableMixin, models.Model):
    """
    Categoria per la galleria fotografica.
    
    Snippet con TranslatableMixin per supporto multilingua.
    Usato nei filtri della galleria e nel GalleryImageBlock.
    """
    
    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=100,
        help_text=_("Nome della categoria (es. 'Raduni', 'Escursioni')"),
    )
    
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=100,
        help_text=_("Identificatore URL-friendly (es. 'raduni', 'escursioni')"),
    )
    
    icon = models.CharField(
        verbose_name=_("Icona FontAwesome"),
        max_length=50,
        blank=True,
        default="fas fa-images",
        help_text=_("Classe FontAwesome (es. 'fas fa-users', 'fas fa-mountain')"),
    )
    
    sort_order = models.PositiveIntegerField(
        verbose_name=_("Ordine"),
        default=0,
        help_text=_("Ordine di visualizzazione nei filtri"),
    )
    
    panels: ClassVar[list] = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("icon"),
        FieldPanel("sort_order"),
    ]
    
    class Meta:
        verbose_name = _("Categoria Galleria")
        verbose_name_plural = _("Categorie Galleria")
        ordering = ["sort_order", "name"]
        unique_together = [("translation_key", "locale")]
    
    def __str__(self) -> str:
        return self.name


@register_snippet
class SimpleCarousel(TranslatableMixin, ClusterableModel):
    """
    Carousel semplice senza StreamField nelle slide.
    
    Evita il bug MultiValueDictKeyError di CodeRedCMS 6.0 con Wagtail 7.
    Usa solo campi semplici: immagine, titolo, sottotitolo, link.
    """
    
    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=255,
        help_text=_("Nome identificativo del carousel."),
    )
    
    show_controls = models.BooleanField(
        verbose_name=_("Mostra controlli"),
        default=True,
        help_text=_("Mostra frecce di navigazione."),
    )
    
    show_indicators = models.BooleanField(
        verbose_name=_("Mostra indicatori"),
        default=True,
        help_text=_("Mostra pallini indicatori sotto il carousel."),
    )
    
    autoplay = models.BooleanField(
        verbose_name=_("Autoplay"),
        default=True,
        help_text=_("Cambia slide automaticamente."),
    )
    
    interval = models.PositiveIntegerField(
        verbose_name=_("Intervallo (ms)"),
        default=5000,
        help_text=_("Tempo tra le slide in millisecondi."),
    )
    
    panels: ClassVar[list] = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("show_controls"),
                FieldPanel("show_indicators"),
                FieldPanel("autoplay"),
                FieldPanel("interval"),
            ],
            heading=_("Impostazioni Carousel"),
        ),
        InlinePanel("slides", label=_("Slide")),
    ]
    
    class Meta:
        verbose_name = _("Carousel Semplice")
        verbose_name_plural = _("Carousel Semplici")
        unique_together = [("translation_key", "locale")]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.locale})"


class SimpleCarouselSlide(Orderable):
    """
    Slide per SimpleCarousel.
    
    Usa solo campi semplici senza StreamField per evitare bug.
    """
    
    carousel = ParentalKey(
        SimpleCarousel,
        on_delete=models.CASCADE,
        related_name="slides",
    )
    
    image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Immagine"),
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
        help_text=_("Immagine di sfondo della slide (consigliato: 1920x800)."),
    )
    
    title = models.CharField(
        verbose_name=_("Titolo"),
        max_length=255,
        blank=True,
        help_text=_("Titolo sovrapposto all'immagine."),
    )
    
    subtitle = models.CharField(
        verbose_name=_("Sottotitolo"),
        max_length=500,
        blank=True,
        help_text=_("Testo descrittivo sotto il titolo."),
    )
    
    button_text = models.CharField(
        verbose_name=_("Testo pulsante"),
        max_length=100,
        blank=True,
        help_text=_("Testo del pulsante CTA (lascia vuoto per nascondere)."),
    )
    
    button_url = models.CharField(
        verbose_name=_("URL pulsante"),
        max_length=500,
        blank=True,
        help_text=_("Link del pulsante (può essere URL esterno o percorso interno)."),
    )
    
    overlay_opacity = models.PositiveIntegerField(
        verbose_name=_("Opacità overlay"),
        default=40,
        help_text=_("Opacità dell'overlay scuro (0-100)."),
    )
    
    panels: ClassVar[list] = [
        FieldPanel("image"),
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("button_text"),
        FieldPanel("button_url"),
        FieldPanel("overlay_opacity"),
    ]
    
    class Meta:
        verbose_name = _("Slide")
        verbose_name_plural = _("Slide")
        ordering = ["sort_order"]
