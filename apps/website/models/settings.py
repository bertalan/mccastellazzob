"""
MC Castellazzo - Site Settings
==============================
Impostazioni globali del sito (solo campi non-SEO).

NOTE: I dati SEO e organizzazione sono in Settings > SEO (wagtailseo.SeoSettings)
- struct_org_type, struct_org_name
- struct_org_logo, struct_org_image
- struct_org_phone, struct_org_address_*
- struct_org_geo_lat/lng
- struct_org_hours, struct_org_actions

Questo modello contiene SOLO:
- Logo/Favicon (per header/branding)
- URL Social Media
- Testo Footer
- Altre impostazioni visive

Per accedere ai dati organizzazione usare:
    from apps.core.seo import get_organization_data, get_seo_settings
    org_data = get_organization_data(page)
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon="cog")
class SiteSettings(BaseSiteSetting):
    """
    Impostazioni globali del sito, accessibili da tutti i template.
    
    NON duplica i campi SEO già presenti in wagtailseo.SeoSettings.
    Per i dati organizzazione (nome, indirizzo, telefono, ecc.)
    usare Settings > SEO in Wagtail Admin.
    """
    
    # === BRANDING ===
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
        help_text=_("Logo per header e navbar"),
    )
    
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Favicon"),
        help_text=_("Icona per browser tab (32x32px consigliato)"),
    )
    
    # === SOCIAL MEDIA ===
    facebook_url = models.URLField(
        _("Facebook URL"),
        blank=True,
        help_text=_("URL pagina Facebook"),
    )
    
    instagram_url = models.URLField(
        _("Instagram URL"),
        blank=True,
        help_text=_("URL profilo Instagram"),
    )
    
    youtube_url = models.URLField(
        _("YouTube URL"),
        blank=True,
        help_text=_("URL canale YouTube"),
    )
    
    # === FOOTER ===
    footer_text = models.CharField(
        _("Testo Footer"),
        max_length=255,
        blank=True,
        default="© MC Castellazzo Bormida - Tutti i diritti riservati",
        help_text=_("Copyright o altro testo per il footer"),
    )
    
    # === MOTOCLUB INFO ===
    founding_year = models.PositiveIntegerField(
        _("Anno di fondazione"),
        default=1933,
        help_text=_("Anno di fondazione del motoclub (es. 1933)"),
    )
    
    sport = models.CharField(
        _("Sport"),
        max_length=100,
        default="Motorcycling",
        help_text=_("Tipo di sport praticato (es. Motorcycling)"),
    )
    
    member_of_name = models.CharField(
        _("Federazione di appartenenza"),
        max_length=200,
        default="FMI - Federazione Motociclistica Italiana",
        blank=True,
        help_text=_("Nome della federazione sportiva di appartenenza"),
    )
    
    # === PANELS ===
    panels = [
        HelpPanel(
            content=_(
                "<strong>Nota:</strong> Per modificare nome organizzazione, indirizzo, "
                "telefono e altri dati SEO vai in <strong>Settings > SEO</strong>."
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("logo"),
                FieldPanel("favicon"),
            ],
            heading=_("Branding"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("youtube_url"),
            ],
            heading=_("Social Media"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("founding_year"),
                FieldPanel("sport"),
                FieldPanel("member_of_name"),
                FieldPanel("footer_text"),
            ],
            heading=_("Footer & Info"),
        ),
    ]
    
    class Meta:
        verbose_name = _("Impostazioni Sito")
        verbose_name_plural = _("Impostazioni Sito")
