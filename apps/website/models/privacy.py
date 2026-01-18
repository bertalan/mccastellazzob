"""
MC Castellazzo - Privacy Page Model  
====================================
Pagina Privacy Policy semplice.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from apps.core.seo import JsonLdMixin, clean_html


class PrivacyPage(JsonLdMixin, Page):
    """
    Pagina Privacy Policy - schema.org WebPage.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    body = RichTextField(
        _("Contenuto"),
        blank=True,
    )
    
    # === Wagtail Config ===
    template = "website/pages/privacy_page.jinja2"
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]
    
    class Meta:
        verbose_name = _("Privacy Policy")
        verbose_name_plural = _("Privacy Policy")
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "WebPage"
    
    def get_json_ld_data(self, request=None) -> dict:
        return {
            "name": self.title,
            "description": clean_html(self.intro) if self.intro else "",
            "url": self.full_url,
        }
