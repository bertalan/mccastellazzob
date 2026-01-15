"""
MC Castellazzo - Site Settings
==============================
Impostazioni globali del sito.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


@register_setting
class SiteSettings(BaseGenericSetting):
    """
    Impostazioni globali del sito, accessibili da tutti i template.
    """
    
    # Informazioni Organizzazione (per Schema.org)
    organization_name = models.CharField(
        _("Nome Organizzazione"),
        max_length=100,
        default="MC Castellazzo Bormida",
        help_text=_("Nome ufficiale dell'organizzazione"),
    )
    
    organization_alternate_name = models.CharField(
        _("Nome Alternativo"),
        max_length=150,
        blank=True,
        default="Moto Club Castellazzo Bormida",
        help_text=_("Nome esteso o alternativo"),
    )
    
    organization_founding_year = models.PositiveIntegerField(
        _("Anno Fondazione"),
        null=True,
        blank=True,
        default=1933,
    )
    
    organization_description = models.TextField(
        _("Descrizione Organizzazione"),
        blank=True,
        default="Moto Club fondato nel 1933, affiliato FMI",
        help_text=_("Breve descrizione per Schema.org"),
    )
    
    # Località (per Schema.org address)
    organization_city = models.CharField(
        _("Città"),
        max_length=100,
        default="Castellazzo Bormida",
    )
    
    organization_region = models.CharField(
        _("Regione"),
        max_length=100,
        default="Piemonte",
    )
    
    organization_postal_code = models.CharField(
        _("CAP"),
        max_length=10,
        default="15073",
    )
    
    organization_country = models.CharField(
        _("Paese"),
        max_length=2,
        default="IT",
        help_text=_("Codice ISO 2 lettere (es. IT, FR, DE)"),
    )
    
    organization_street_address = models.CharField(
        _("Indirizzo"),
        max_length=200,
        blank=True,
        default="Via San Francesco d'Assisi, 1",
        help_text=_("Indirizzo della sede"),
    )
    
    organization_email = models.EmailField(
        _("Email"),
        blank=True,
        default="mccastellazzob@gmail.com",
    )
    
    organization_phone = models.CharField(
        _("Telefono"),
        max_length=30,
        blank=True,
        default="+39 335 789 9368",
    )
    
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )
    
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Favicon"),
    )
    
    # Social Media
    facebook_url = models.URLField(
        _("Facebook URL"),
        blank=True,
    )
    
    instagram_url = models.URLField(
        _("Instagram URL"),
        blank=True,
    )
    
    youtube_url = models.URLField(
        _("YouTube URL"),
        blank=True,
    )
    
    # Footer
    footer_text = models.CharField(
        _("Testo Footer"),
        max_length=255,
        blank=True,
        default="© MC Castellazzo Bormida - Tutti i diritti riservati",
    )
    
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("organization_name"),
                FieldPanel("organization_alternate_name"),
                FieldPanel("organization_founding_year"),
                FieldPanel("organization_description"),
            ],
            heading=_("Informazioni Organizzazione"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("organization_street_address"),
                FieldPanel("organization_city"),
                FieldPanel("organization_region"),
                FieldPanel("organization_postal_code"),
                FieldPanel("organization_country"),
                FieldPanel("organization_email"),
                FieldPanel("organization_phone"),
            ],
            heading=_("Località e Contatti"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("logo"),
                FieldPanel("favicon"),
            ],
            heading=_("Logo e Favicon"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("youtube_url"),
            ],
            heading=_("Social Media"),
        ),
        FieldPanel("footer_text"),
    ]
    
    class Meta:
        verbose_name = _("Impostazioni Sito")
        verbose_name_plural = _("Impostazioni Sito")
