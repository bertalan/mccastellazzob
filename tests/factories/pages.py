"""
MC Castellazzo - Page Factories
"""
import factory
from factory.django import DjangoModelFactory
from wagtail.models import Page

from apps.website.models import (
    HomePage,
    TimelinePage,
    AboutPage,
    BoardPage,
    TransparencyPage,
    ContactPage,
    EventsPage,
    EventDetailPage,
    EventsArchivePage,
)


class HomePageFactory(DjangoModelFactory):
    """Factory for HomePage."""
    
    class Meta:
        model = HomePage
    
    title = "MC Castellazzo"
    slug = factory.Sequence(lambda n: f"home-{n}")
    organization_name = "MC Castellazzo"
    description = "<p>Motoclub dal 1975</p>"
    street_address = "Via Roma 1"
    city = "Torino"
    region = "Piedmont"
    country = "IT"
    postal_code = "10100"
    telephone = "+39 011 1234567"
    email = "info@mccastellazzob.com"
    founding_date = factory.Faker("date_this_century")
    hero_title = "Benvenuti al MC Castellazzo"
    hero_subtitle = "Passione per le moto dal 1975"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Ensure proper Wagtail page creation."""
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        
        if parent:
            parent.add_child(instance=instance)
        else:
            # Add to root
            root = Page.objects.filter(depth=1).first()
            if root:
                root.add_child(instance=instance)
        
        return instance


class TimelinePageFactory(DjangoModelFactory):
    """Factory for TimelinePage."""
    
    class Meta:
        model = TimelinePage
    
    title = "Timeline"
    slug = factory.Sequence(lambda n: f"timeline-{n}")
    intro = "La nostra storia attraverso gli anni"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class AboutPageFactory(DjangoModelFactory):
    """Factory for AboutPage."""
    
    class Meta:
        model = AboutPage
    
    title = "Chi Siamo"
    slug = factory.Sequence(lambda n: f"chi-siamo-{n}")
    intro = "<p>Scopri il nostro club</p>"
    body = "<p>Contenuto della pagina chi siamo</p>"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class BoardPageFactory(DjangoModelFactory):
    """Factory for BoardPage."""
    
    class Meta:
        model = BoardPage
    
    title = "Consiglio Direttivo"
    slug = factory.Sequence(lambda n: f"consiglio-{n}")
    intro = "<p>Il nostro team direttivo</p>"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class TransparencyPageFactory(DjangoModelFactory):
    """Factory for TransparencyPage."""
    
    class Meta:
        model = TransparencyPage
    
    title = "Trasparenza"
    slug = factory.Sequence(lambda n: f"trasparenza-{n}")
    intro = "<p>Documenti ufficiali</p>"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class ContactPageFactory(DjangoModelFactory):
    """Factory for ContactPage."""
    
    class Meta:
        model = ContactPage
    
    title = "Contatti"
    slug = factory.Sequence(lambda n: f"contatti-{n}")
    intro = "<p>Contattaci</p>"
    address = "Via Roma 1, Torino"
    latitude = 45.0703
    longitude = 7.6869
    phone = "+39 011 1234567"
    email = "info@mccastellazzob.com"
    show_contact_form = True
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class EventsPageFactory(DjangoModelFactory):
    """Factory for EventsPage."""
    
    class Meta:
        model = EventsPage
    
    title = "Eventi"
    slug = factory.Sequence(lambda n: f"eventi-{n}")
    intro = "<p>I nostri eventi</p>"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class EventDetailPageFactory(DjangoModelFactory):
    """Factory for EventDetailPage."""
    
    class Meta:
        model = EventDetailPage
    
    title = factory.Sequence(lambda n: f"Evento {n}")
    slug = factory.Sequence(lambda n: f"evento-{n}")
    event_name = factory.Sequence(lambda n: f"Raduno Moto {n}")
    start_date = factory.Faker("future_datetime", end_date="+365d")
    location_name = "Piazza Castello"
    location_address = "Piazza Castello, Torino"
    location_lat = 45.0715
    location_lon = 7.6858
    description = "<p>Descrizione dell'evento</p>"
    event_status = "EventScheduled"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance


class EventsArchivePageFactory(DjangoModelFactory):
    """Factory for EventsArchivePage."""
    
    class Meta:
        model = EventsArchivePage
    
    title = "Archivio Eventi"
    slug = factory.Sequence(lambda n: f"archivio-eventi-{n}")
    intro = "<p>Archivio storico</p>"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        instance = model_class(**kwargs)
        if parent:
            parent.add_child(instance=instance)
        return instance
