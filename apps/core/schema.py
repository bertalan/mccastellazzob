"""
MC Castellazzo - Schema.org Helpers (DEPRECATED)
=================================================
NOTA: Questo modulo è deprecato. Usare apps.core.seo invece.

Questo file mantiene la backward compatibility importando dal nuovo modulo.
I nuovi sviluppi dovrebbero usare direttamente apps.core.seo.

Migration Guide:
----------------
OLD:
    from apps.core.schema import SchemaOrgMixin, clean_html
    class MyPage(SchemaOrgMixin, Page):
        def get_schema_org_type(self): return "Event"
        def get_schema_org_data(self): return {...}

NEW:
    from apps.core.seo import JsonLdMixin, clean_html
    class MyPage(JsonLdMixin, Page):
        def get_json_ld_type(self): return "Event"
        def get_json_ld_data(self, request=None): return {...}
"""
import warnings

# Re-export everything from the new module for backward compatibility
from apps.core.seo import (
    # Core utilities
    clean_html,
    SchemaEncoder,
    # Wagtailseo integration
    get_seo_settings,
    get_social_urls,
    get_organization_data,
    # Mixin (JsonLdMixin is the new name)
    JsonLdMixin,
    # Helper functions
    postal_address,
    geo_coordinates,
    place,
    contact_point,
    event,
    person,
    image_object,
    article,
    item_list,
    list_item,
    breadcrumb_list,
    web_page,
    sports_organization,
    # Multilingual helpers
    get_page_url_for_locale,
    get_alternate_urls,
)

# Legacy alias - deprecato ma mantenuto per retrocompatibilità
SchemaOrgMixin = JsonLdMixin


# All exported for compatibility
__all__ = [
    "clean_html",
    "SchemaEncoder",
    "get_seo_settings",
    "get_social_urls",
    "get_organization_data",
    "JsonLdMixin",
    "SchemaOrgMixin",
    "postal_address",
    "geo_coordinates",
    "place",
    "contact_point",
    "event",
    "person",
    "image_object",
    "article",
    "item_list",
    "list_item",
    "breadcrumb_list",
    "web_page",
    "sports_organization",
    "get_page_url_for_locale",
    "get_alternate_urls",
]

