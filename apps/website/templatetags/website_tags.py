"""
Template tags for website navigation.

mccastellazzob.com - Moto Club Castellazzo Bormida
Template tags per navbar e footer multilingua.
"""

from django import template
from django.utils.translation import get_language
from wagtail.models import Locale

from apps.website.models import Navbar, Footer

register = template.Library()


def get_current_locale():
    """Get the current Wagtail locale based on Django language."""
    lang_code = get_language() or "it"
    try:
        return Locale.objects.get(language_code=lang_code)
    except Locale.DoesNotExist:
        return Locale.objects.get(language_code="it")


@register.simple_tag
def get_navbar():
    """
    Restituisce la navbar attiva per la lingua corrente.

    Returns:
        Navbar object or None
    """
    locale = get_current_locale()
    return Navbar.objects.filter(is_active=True, locale=locale).first()


@register.simple_tag
def get_footer():
    """
    Restituisce il footer attivo per la lingua corrente.

    Returns:
        Footer object or None
    """
    locale = get_current_locale()
    return Footer.objects.filter(is_active=True, locale=locale).first()


@register.inclusion_tag("website/tags/navbar.html")
def render_navbar():
    """
    Renderizza la navbar principale.

    Returns:
        Contesto per il template navbar.html.
    """
    navbar = get_navbar()
    return {"navbar": navbar}


@register.inclusion_tag("website/tags/footer.html")
def render_footer():
    """
    Renderizza il footer principale.

    Returns:
        Contesto per il template footer.html.
    """
    footer = get_footer()
    return {"footer": footer}
