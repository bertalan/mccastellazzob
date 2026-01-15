"""
MC Castellazzo - HomePage Model
================================
schema.org Organization
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.core.schema import SchemaOrgMixin, postal_address, contact_point
from apps.website.blocks import (
    HeroSliderBlock,
    HeroCountdownBlock,
    StatsBlock,
    SectionCardsGridBlock,
    CTABlock,
    GalleryBlock,
    ArticleBlock,
)


class HomePage(SchemaOrgMixin, Page):
    """
    Homepage del sito - schema.org Organization.
    
    Campi secondo schema.org:
    - name: Nome organizzazione
    - logo: Logo
    - url: URL sito
    - description: Descrizione
    - address: PostalAddress
    - contactPoint: ContactPoint
    - foundingDate: Data fondazione
    - knowsAbout: Motoclub
    """
    
    # === Campi Organization ===
    organization_name = models.CharField(
        _("Nome organizzazione"),
        max_length=255,
        default="MC Castellazzo",
    )
    
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )
    
    description = RichTextField(
        _("Descrizione"),
        blank=True,
    )
    
    # Address (PostalAddress)
    street_address = models.CharField(
        _("Indirizzo"),
        max_length=255,
        blank=True,
    )
    city = models.CharField(
        _("Città"),
        max_length=100,
        default="Torino",
    )
    region = models.CharField(
        _("Regione"),
        max_length=100,
        default="Piedmont",
    )
    country = models.CharField(
        _("Paese"),
        max_length=2,
        default="IT",
    )
    postal_code = models.CharField(
        _("CAP"),
        max_length=10,
        blank=True,
    )
    
    # ContactPoint
    telephone = models.CharField(
        _("Telefono"),
        max_length=30,
        blank=True,
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
    )
    
    # Founding date
    founding_date = models.DateField(
        _("Data fondazione"),
        null=True,
        blank=True,
    )
    
    # Hero section
    hero_title = models.CharField(
        _("Titolo hero"),
        max_length=255,
        blank=True,
    )
    hero_subtitle = models.CharField(
        _("Sottotitolo hero"),
        max_length=500,
        blank=True,
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine hero"),
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
                FieldPanel("organization_name"),
                FieldPanel("logo"),
                FieldPanel("description"),
                FieldPanel("founding_date"),
            ],
            heading=_("Informazioni Organizzazione"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("street_address"),
                FieldPanel("city"),
                FieldPanel("region"),
                FieldPanel("country"),
                FieldPanel("postal_code"),
            ],
            heading=_("Indirizzo"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("telephone"),
                FieldPanel("email"),
            ],
            heading=_("Contatti"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_image"),
            ],
            heading=_("Hero Section"),
        ),
        FieldPanel("body"),
    ]
    
    class Meta:
        verbose_name = _("Homepage")
        verbose_name_plural = _("Homepage")
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "Organization"
    
    def get_schema_org_data(self) -> dict:
        data = {
            "name": self.organization_name,
            "url": self.full_url,
            "knowsAbout": "Motoclub",
        }
        
        if self.logo:
            data["logo"] = self.logo.get_rendition("original").url
        
        if self.description:
            data["description"] = self.description
        
        data["address"] = postal_address(
            street=self.street_address,
            city=self.city,
            region=self.region,
            country=self.country,
            postal_code=self.postal_code,
        )
        
        if self.telephone or self.email:
            data["contactPoint"] = contact_point(
                telephone=self.telephone,
                email=self.email,
            )
        
        if self.founding_date:
            data["foundingDate"] = self.founding_date.isoformat()
        
        return data
