"""
Snippet models for the website.

mccastellazzob.com - Moto Club Castellazzo Bormida
Snippet multilingua per navbar e footer.
"""

from __future__ import annotations

from typing import ClassVar

from coderedcms.blocks import BaseBlock
from coderedcms.blocks import BaseLinkBlock
from coderedcms.blocks import LinkStructValue
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
    """

    class Meta:
        icon = "link"
        label = _("Link")
        value_class = LinkStructValue


class NavbarDropdownBlock(BaseBlock):
    """
    Blocco per dropdown nella navbar con link multipli.
    """

    title = blocks.CharBlock(
        max_length=255,
        required=True,
        label=_("Titolo dropdown"),
    )

    links = blocks.ListBlock(
        NavbarLinkBlock(),
        label=_("Link nel dropdown"),
    )

    class Meta:
        icon = "list-ul"
        label = _("Dropdown")
        template = "website/blocks/navbar_dropdown.html"


@register_snippet
class Navbar(TranslatableMixin, models.Model):
    """
    Navbar multilingua.

    Snippet con TranslatableMixin per supporto IT/EN/FR.
    Ogni lingua ha la propria versione della navbar.
    """

    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=255,
        help_text=_("Nome identificativo della navbar."),
    )

    menu_items = StreamField(
        [
            ("link", NavbarLinkBlock()),
            ("dropdown", NavbarDropdownBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Voci menu"),
    )

    panels: ClassVar[list] = [
        FieldPanel("name"),
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

    Snippet con TranslatableMixin per supporto IT/EN/FR.
    Ogni lingua ha la propria versione del footer.
    """

    name = models.CharField(
        verbose_name=_("Nome"),
        max_length=255,
        help_text=_("Nome identificativo del footer."),
    )

    content = StreamField(
        [
            ("link", NavbarLinkBlock()),
            (
                "text",
                blocks.RichTextBlock(
                    features=["bold", "italic", "link"],
                    label=_("Testo"),
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Contenuto footer"),
    )

    panels: ClassVar[list] = [
        FieldPanel("name"),
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name = _("Footer")
        verbose_name_plural = _("Footer")
        unique_together = [("translation_key", "locale")]

    def __str__(self) -> str:
        return f"{self.name} ({self.locale})"
