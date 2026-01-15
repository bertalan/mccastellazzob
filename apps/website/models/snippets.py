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
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import TranslatableMixin
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
