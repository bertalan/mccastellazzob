"""
Website models package.

mccastellazzob.com - Moto Club Castellazzo Bormida
Contiene modelli pagina e snippet.
"""

from apps.website.models.pages import ArticleIndexPage
from apps.website.models.pages import ArticlePage
from apps.website.models.pages import EventIndexPage
from apps.website.models.pages import EventPage
from apps.website.models.pages import FormConfirmEmail
from apps.website.models.pages import FormPage
from apps.website.models.pages import FormPageField
from apps.website.models.pages import LocationIndexPage
from apps.website.models.pages import LocationPage
from apps.website.models.pages import WebPage
from apps.website.models.snippets import Footer
from apps.website.models.snippets import Navbar


__all__ = [
    "ArticlePage",
    "ArticleIndexPage",
    "EventPage",
    "EventIndexPage",
    "LocationPage",
    "LocationIndexPage",
    "WebPage",
    "FormPage",
    "FormPageField",
    "FormConfirmEmail",
    "Navbar",
    "Footer",
]
