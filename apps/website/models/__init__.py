"""
MC Castellazzo - Page Models
=============================
Modelli pagine Wagtail con supporto schema.org.
"""
from .home import HomePage
from .timeline import TimelinePage
from .about import AboutPage, BoardPage, TransparencyPage, ContactPage
from .events import EventsPage, EventDetailPage, EventsArchivePage
from .gallery import GalleryPage, GalleryImage
from .privacy import PrivacyPage
from .settings import SiteSettings
from .snippets import Navbar, Footer

__all__ = [
    "HomePage",
    "TimelinePage",
    "AboutPage",
    "BoardPage",
    "TransparencyPage",
    "ContactPage",
    "EventsPage",
    "EventDetailPage",
    "EventsArchivePage",
    "GalleryPage",
    "GalleryImage",
    "PrivacyPage",
    "SiteSettings",
    "Navbar",
    "Footer",
]
