"""
Custom template tags for the website.

mccastellazzob.com - Moto Club Castellazzo Bormida
Template tags per navbar, footer e altre funzionalità.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.utils.translation import get_language
from wagtail.models import Locale


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.website.models.snippets import Footer
    from apps.website.models.snippets import Navbar


register = template.Library()


@register.simple_tag
def get_website_navbars() -> QuerySet[Navbar]:
    """
    Restituisce tutte le navbar per la lingua corrente.

    Returns:
        QuerySet di Navbar filtrate per locale corrente.
    """
    from apps.website.models.snippets import Navbar

    current_language = get_language() or "it"

    try:
        locale = Locale.objects.get(language_code=current_language)
        return Navbar.objects.filter(locale=locale)
    except Locale.DoesNotExist:
        return Navbar.objects.all()


@register.simple_tag
def get_website_footers() -> QuerySet[Footer]:
    """
    Restituisce tutti i footer per la lingua corrente.

    Returns:
        QuerySet di Footer filtrati per locale corrente.
    """
    from apps.website.models.snippets import Footer

    current_language = get_language() or "it"

    try:
        locale = Locale.objects.get(language_code=current_language)
        return Footer.objects.filter(locale=locale)
    except Locale.DoesNotExist:
        return Footer.objects.all()


@register.inclusion_tag("website/tags/navbar.html")
def render_navbar() -> dict:
    """
    Renderizza la navbar principale.

    Returns:
        Contesto per il template navbar.html.
    """
    navbars = get_website_navbars()
    return {"navbars": navbars}


@register.inclusion_tag("website/tags/footer.html")
def render_footer() -> dict:
    """
    Renderizza il footer principale.

    Returns:
        Contesto per il template footer.html.
    """
    footers = get_website_footers()
    return {"footers": footers}
