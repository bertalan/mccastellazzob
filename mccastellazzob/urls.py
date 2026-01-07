"""
URL configuration for mccastellazzob project.

mccastellazzob.com - Moto Club Castellazzo Bormida
Configurazione i18n: IT (default, no prefix), EN (/en/), FR (/fr/)
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.website.views import localized_search


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

# i18n patterns - IT senza prefisso, EN/FR con prefisso
urlpatterns += i18n_patterns(
    path("search/", localized_search, name="search"),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

# Static e media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
