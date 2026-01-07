"""
Page factories.

mccastellazzob.com - Moto Club Castellazzo Bormida
Factories per modelli pagina.
"""

import factory
from wagtail.models import Locale
from wagtail.models import Page

from apps.website.models.pages import ArticleIndexPage
from apps.website.models.pages import ArticlePage
from apps.website.models.pages import EventIndexPage
from apps.website.models.pages import EventPage
from apps.website.models.pages import WebPage


class WebPageFactory(factory.django.DjangoModelFactory):
    """Factory per creare WebPage."""

    class Meta:
        model = WebPage

    title = factory.Sequence(lambda n: f"Web Page {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    depth = 2
    path = factory.Sequence(lambda n: f"0001000{n:04d}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class ArticleIndexPageFactory(factory.django.DjangoModelFactory):
    """Factory per creare ArticleIndexPage."""

    class Meta:
        model = ArticleIndexPage

    title = factory.Sequence(lambda n: f"Article Index {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    depth = 2
    path = factory.Sequence(lambda n: f"0001001{n:04d}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class ArticlePageFactory(factory.django.DjangoModelFactory):
    """Factory per creare ArticlePage."""

    class Meta:
        model = ArticlePage

    title = factory.Sequence(lambda n: f"Article {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    depth = 3
    path = factory.Sequence(lambda n: f"000100010{n:03d}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class EventIndexPageFactory(factory.django.DjangoModelFactory):
    """Factory per creare EventIndexPage."""

    class Meta:
        model = EventIndexPage

    title = factory.Sequence(lambda n: f"Event Index {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    depth = 2
    path = factory.Sequence(lambda n: f"0001002{n:04d}")

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale


class EventPageFactory(factory.django.DjangoModelFactory):
    """Factory per creare EventPage."""

    class Meta:
        model = EventPage

    title = factory.Sequence(lambda n: f"Event {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    depth = 3
    path = factory.Sequence(lambda n: f"000100020{n:03d}")
    address = factory.Faker("address", locale="it_IT")
    location = "44.8566,8.6144"  # Castellazzo Bormida

    @factory.lazy_attribute
    def locale(self):
        locale, _ = Locale.objects.get_or_create(language_code="it")
        return locale
