"""
MC Castellazzo - URL Configuration
==================================
Supporto multilingua con prefix /it/, /fr/, /es/, /en/
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from coderedcms import admin_urls as crx_admin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Django admin
    path("django-admin/", admin.site.urls),
    # Wagtail admin (usa CodeRedCMS admin_urls che include import_index)
    path("admin/", include(crx_admin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Allauth (frontend auth)
    path("accounts/", include("allauth.urls")),
]

# URL patterns con prefisso lingua - Wagtail serve le pagine
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
    prefix_default_language=True,
)

# Static and media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
