"""
MC Castellazzo - About Pages Models
====================================
Pagine Chi Siamo con sottopagine:
- AboutPage (schema.org AboutPage)
- BoardPage (Consiglio Direttivo - schema.org Organization with members)
- TransparencyPage (Trasparenza - schema.org WebPage)
- ContactPage (Contatti - schema.org ContactPage)
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.core.schema import SchemaOrgMixin, person, postal_address
from apps.core.maps import get_default_location
from apps.website.blocks import MemberBlock, DocumentBlock, MapBlock, StatsBlock, ValuesBlock, TimelineBlock


class AboutPage(SchemaOrgMixin, Page):
    """
    Pagina Chi Siamo principale - schema.org AboutPage.
    """
    
    # Hero fields
    hero_title = models.CharField(
        _("Titolo Hero"),
        max_length=100,
        blank=True,
        help_text=_("Titolo principale nell'hero section"),
    )
    
    hero_subtitle = models.CharField(
        _("Sottotitolo Hero"),
        max_length=200,
        blank=True,
        help_text=_("Sottotitolo nell'hero section"),
    )
    
    # Statistics
    founding_year = models.PositiveIntegerField(
        _("Anno di fondazione"),
        default=1933,
    )
    
    members_count = models.PositiveIntegerField(
        _("Numero soci attivi"),
        default=250,
    )
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    body = RichTextField(
        _("Contenuto"),
        blank=True,
    )
    
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine"),
    )
    
    # Timeline storica
    timeline = StreamField(
        [
            ("timeline", TimelineBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Timeline Storica"),
    )
    
    # Milestones - statistiche del motoclub
    milestones = StreamField(
        [
            ("stats", StatsBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Traguardi / Statistiche"),
    )
    
    # Values - valori del motoclub  
    values = StreamField(
        [
            ("values", ValuesBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("I Nostri Valori"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/about_page.jinja2"
    subpage_types = ["website.BoardPage", "website.TransparencyPage", "website.ContactPage"]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
            ],
            heading=_("Hero Section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("founding_year"),
                FieldPanel("members_count"),
            ],
            heading=_("Statistiche"),
        ),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("timeline"),
        FieldPanel("milestones"),
        FieldPanel("values"),
    ]
    
    class Meta:
        verbose_name = _("Chi Siamo")
        verbose_name_plural = _("Chi Siamo")
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "AboutPage"
    
    def get_schema_org_data(self) -> dict:
        data = {
            "name": self.title,
            "url": self.full_url,
        }
        if self.intro:
            data["description"] = self.intro
        if self.image:
            data["image"] = self.image.get_rendition("original").url
        return data


class BoardPage(SchemaOrgMixin, Page):
    """
    Pagina Consiglio Direttivo - schema.org Organization con members.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    members = StreamField(
        [
            ("member", MemberBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Membri"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/board_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("members"),
    ]
    
    class Meta:
        verbose_name = _("Consiglio Direttivo")
        verbose_name_plural = _("Consiglio Direttivo")
    
    def get_members_list(self):
        """Ritorna la lista dei membri."""
        members_list = []
        for block in self.members:
            if block.block_type == "member":
                members_list.append(block.value)
        return members_list
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "Organization"
    
    def get_schema_org_data(self) -> dict:
        members = []
        for m in self.get_members_list():
            members.append(person(
                name=m.get("name", ""),
                job_title=m.get("role", ""),
                image_url=m.get("image").get_rendition("fill-300x300").url if m.get("image") else "",
            ))
        
        return {
            "name": self.title,
            "url": self.full_url,
            "member": members,
        }


class TransparencyPage(SchemaOrgMixin, Page):
    """
    Pagina Trasparenza - schema.org WebPage con documenti allegati.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    documents = StreamField(
        [
            ("document", DocumentBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Documenti"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/transparency_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("documents"),
    ]
    
    class Meta:
        verbose_name = _("Trasparenza")
        verbose_name_plural = _("Trasparenza")
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "WebPage"
    
    def get_schema_org_data(self) -> dict:
        return {
            "name": self.title,
            "url": self.full_url,
            "description": self.intro if self.intro else "",
        }


class ContactPage(SchemaOrgMixin, Page):
    """
    Pagina Contatti - schema.org ContactPage con form e mappa OpenStreetMap.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    # Indirizzo per mappa
    address = models.CharField(
        _("Indirizzo"),
        max_length=500,
        blank=True,
        help_text=_("Indirizzo completo per la mappa"),
    )
    
    latitude = models.FloatField(
        _("Latitudine"),
        null=True,
        blank=True,
    )
    
    longitude = models.FloatField(
        _("Longitudine"),
        null=True,
        blank=True,
    )
    
    # Contatti
    phone = models.CharField(
        _("Telefono"),
        max_length=30,
        blank=True,
    )
    
    email = models.EmailField(
        _("Email"),
        blank=True,
    )
    
    # Form abilitato
    show_contact_form = models.BooleanField(
        _("Mostra form contatto"),
        default=True,
    )
    
    form_success_message = models.CharField(
        _("Messaggio successo form"),
        max_length=255,
        default=_("Grazie per averci contattato!"),
    )
    
    # Note contatti
    phone_note = models.CharField(
        _("Nota telefono"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Chiamaci il giovedì sera'"),
    )
    
    email_note = models.CharField(
        _("Nota email"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Rispondiamo entro 24h'"),
    )
    
    # Orari sede
    opening_hours = models.TextField(
        _("Orari apertura"),
        blank=True,
        help_text=_("Un orario per riga, formato: 'Giorno: HH:MM - HH:MM'"),
    )
    
    opening_hours_note = models.CharField(
        _("Nota orari"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Serata sociale settimanale'"),
    )
    
    # Indicazioni stradali
    map_description = models.CharField(
        _("Descrizione mappa"),
        max_length=255,
        blank=True,
        help_text=_("Testo sotto il titolo 'Dove Trovarci'"),
    )
    
    directions_car = models.CharField(
        _("Indicazioni auto"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Uscita A26 Alessandria Sud, 15 min'"),
    )
    
    directions_train = models.CharField(
        _("Indicazioni treno"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Stazione Alessandria + bus linea 5'"),
    )
    
    directions_parking = models.CharField(
        _("Indicazioni parcheggio"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Ampio parcheggio gratuito disponibile'"),
    )
    
    # CTA
    cta_title = models.CharField(
        _("Titolo CTA"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Pronto a Unirti a Noi?'"),
    )
    
    cta_description = models.CharField(
        _("Descrizione CTA"),
        max_length=255,
        blank=True,
        help_text=_("Es: 'Dal 1933 accogliamo appassionati di moto...'"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/contact_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
            ],
            heading=_("Posizione Mappa"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("phone_note"),
                FieldPanel("email"),
                FieldPanel("email_note"),
            ],
            heading=_("Informazioni Contatto"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("opening_hours"),
                FieldPanel("opening_hours_note"),
            ],
            heading=_("Orari Sede"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("map_description"),
                FieldPanel("directions_car"),
                FieldPanel("directions_train"),
                FieldPanel("directions_parking"),
            ],
            heading=_("Indicazioni Stradali"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_contact_form"),
                FieldPanel("form_success_message"),
            ],
            heading=_("Form Contatto"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
            ],
            heading=_("Call to Action"),
        ),
    ]
    
    class Meta:
        verbose_name = _("Contatti")
        verbose_name_plural = _("Contatti")
    
    def get_map_location(self):
        """Ritorna lat/lon per la mappa, con fallback a Torino."""
        if self.latitude and self.longitude:
            return {"lat": self.latitude, "lon": self.longitude}
        return get_default_location()
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "Organization"
    
    def get_schema_org_data(self) -> dict:
        """
        Schema.org Organization con ContactPoint.
        https://schema.org/Organization
        I dati vengono presi da SiteSettings per evitare testo hardcoded.
        """
        from apps.core.schema import contact_point
        from apps.website.models.settings import SiteSettings
        
        # Carica le impostazioni del sito
        site = self.get_site()
        settings = SiteSettings.load(request_or_site=site) if site else None
        
        # Valori da SiteSettings o fallback
        org_name = settings.organization_name if settings else "MC Castellazzo Bormida"
        org_alternate = settings.organization_alternate_name if settings else ""
        org_founding = str(settings.organization_founding_year) if settings else "1933"
        org_description = settings.organization_description if settings else ""
        org_city = settings.organization_city if settings else "Castellazzo Bormida"
        org_region = settings.organization_region if settings else "Piemonte"
        org_postal_code = settings.organization_postal_code if settings else "15073"
        org_country = settings.organization_country if settings else "IT"
        
        data = {
            "name": org_name,
            "url": site.root_url if site else "",
            "foundingDate": org_founding,
        }
        
        # Logo dall'immagine in SiteSettings
        if settings and settings.logo:
            logo_url = settings.logo.file.url
            # Assicurati che l'URL sia assoluto
            if site and not logo_url.startswith("http"):
                logo_url = site.root_url.rstrip("/") + logo_url
            data["logo"] = logo_url
        
        if org_alternate:
            data["alternateName"] = org_alternate
        if org_description:
            data["description"] = org_description
        
        # Indirizzo
        if self.address:
            data["address"] = postal_address(
                street=self.address,
                city=org_city,
                region=org_region,
                country=org_country,
                postal_code=org_postal_code,
            )
        
        # Coordinate geo
        if self.latitude and self.longitude:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
        
        # Contatti
        if self.phone or self.email:
            data["contactPoint"] = contact_point(
                telephone=self.phone,
                email=self.email,
                contact_type="customer service",
            )
        
        return data
