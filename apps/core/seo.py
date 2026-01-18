"""
MC Castellazzo - SEO & Schema.org Module
==========================================
Modulo centralizzato per gestione SEO e generazione JSON-LD.

ARCHITETTURA:
-------------
1. wagtailseo.SeoSettings → fonte UNICA per dati organizzazione
   - Settings > SEO in Wagtail Admin
   - struct_org_* campi per Organization schema.org
   
2. SiteSettings (apps.website) → solo per campi specifici non-SEO
   - Social media URLs
   - Footer text
   - Impostazioni visive

3. Pagine → usano get_organization_data() per accedere ai dati org
   - Nessuna duplicazione di campi
   - Consistenza multilingua

TIPI SCHEMA.ORG SUPPORTATI:
---------------------------
- Organization / SportsClub (homepage, contatti)
- Event (dettaglio evento)
- EventSeries (lista eventi)
- ItemList (archivio, galleria)
- AboutPage, ContactPage, WebPage
- Article (news, blog)
- BreadcrumbList (navigazione)
- ImageGallery / ImageObject

USO:
----
```python
from apps.core.seo import get_organization_data, clean_html, JsonLdMixin

class MyEventPage(JsonLdMixin, Page):
    def get_json_ld_type(self):
        return "Event"
    
    def get_json_ld_data(self, request=None):
        return {
            "name": self.title,
            "organizer": get_organization_data(self),
            ...
        }
```
"""
import json
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Optional, Union

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


# ============================================================================
# UTILITIES
# ============================================================================

def clean_html(html_content: str) -> str:
    """
    Rimuove i tag HTML e normalizza gli spazi bianchi.
    Essenziale per pulire RichTextField prima di inserirli in JSON-LD.
    
    Args:
        html_content: Stringa con possibile markup HTML
        
    Returns:
        Testo pulito senza tag HTML, spazi normalizzati
        
    Example:
        >>> clean_html('<p data-block-key="abc">Hello  World</p>')
        'Hello World'
    """
    if not html_content:
        return ""
    # Rimuove i tag HTML usando Django's strip_tags
    text = strip_tags(str(html_content))
    # Normalizza spazi multipli, tab, newline
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class SchemaEncoder(json.JSONEncoder):
    """
    JSON Encoder che gestisce tipi Python comuni in schema.org.
    Supporta date, datetime, time, Decimal, e oggetti con metodo as_dict().
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.strftime("%H:%M")
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super().default(obj)


# ============================================================================
# WAGTAILSEO INTEGRATION
# ============================================================================

def get_seo_settings(page_or_site):
    """
    Ottiene SeoSettings di wagtailseo per una pagina o sito.
    
    Args:
        page_or_site: Pagina Wagtail, Site, o oggetto con get_site()
        
    Returns:
        wagtailseo.SeoSettings instance
    """
    from wagtailseo.models import SeoSettings
    
    if hasattr(page_or_site, 'get_site'):
        site = page_or_site.get_site()
    else:
        site = page_or_site
    
    return SeoSettings.for_site(site)


def get_social_urls(page) -> list:
    """
    Ottiene lista URL social da SiteSettings.
    
    Args:
        page: Pagina Wagtail
        
    Returns:
        Lista di URL social per sameAs
    """
    from apps.website.models import SiteSettings
    
    try:
        site = page.get_site()
        settings = SiteSettings.for_site(site)
        
        urls = []
        if settings.facebook_url:
            urls.append(settings.facebook_url)
        if settings.instagram_url:
            urls.append(settings.instagram_url)
        if settings.youtube_url:
            urls.append(settings.youtube_url)
        
        return urls
    except Exception:
        return []


def get_organization_data(
    page,
    include_social: bool = True,
    include_geo: bool = True,
) -> dict:
    """
    Ottiene i dati completi dell'organizzazione da SeoSettings.
    FONTE UNICA per tutti i dati organizzazione nel sito.
    
    Args:
        page: Pagina Wagtail (per ottenere Site)
        include_social: Include sameAs con URL social
        include_geo: Include GeoCoordinates
        
    Returns:
        Dict con dati Organization per JSON-LD
        
    Note:
        I campi vengono da Settings > SEO in Wagtail Admin:
        - struct_org_type, struct_org_name
        - struct_org_logo, struct_org_image
        - struct_org_phone, struct_org_address_*
        - struct_org_geo_lat/lng
        - struct_org_hours, struct_org_actions
    """
    seo = get_seo_settings(page)
    site = page.get_site()
    
    # Tipo org - default SportsClub per un motoclub
    org_type = seo.struct_org_type or "SportsClub"
    
    org_data = {
        "@type": org_type,
        "name": seo.struct_org_name or site.site_name,
        "url": site.root_url,
    }
    
    # Logo
    if seo.struct_org_logo:
        try:
            logo_url = seo.struct_org_logo.get_rendition("original").url
            # Assicura URL assoluto
            if not logo_url.startswith('http'):
                logo_url = site.root_url.rstrip('/') + logo_url
            org_data["logo"] = {
                "@type": "ImageObject",
                "url": logo_url,
            }
        except Exception:
            pass
    
    # Immagine organizzazione
    if seo.struct_org_image:
        try:
            image_url = seo.struct_org_image.get_rendition("fill-1200x630").url
            if not image_url.startswith('http'):
                image_url = site.root_url.rstrip('/') + image_url
            org_data["image"] = image_url
        except Exception:
            pass
    
    # Indirizzo
    if seo.struct_org_address_street:
        org_data["address"] = {
            "@type": "PostalAddress",
            "streetAddress": seo.struct_org_address_street,
        }
        if seo.struct_org_address_locality:
            org_data["address"]["addressLocality"] = seo.struct_org_address_locality
        if seo.struct_org_address_region:
            org_data["address"]["addressRegion"] = seo.struct_org_address_region
        if seo.struct_org_address_postal:
            org_data["address"]["postalCode"] = seo.struct_org_address_postal
        if seo.struct_org_address_country:
            org_data["address"]["addressCountry"] = seo.struct_org_address_country
    
    # Coordinate geografiche
    if include_geo and seo.struct_org_geo_lat and seo.struct_org_geo_lng:
        org_data["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(seo.struct_org_geo_lat),
            "longitude": float(seo.struct_org_geo_lng),
        }
    
    # ContactPoint con telefono e orari disponibilità
    # (openingHoursSpecification non è valido a root per SportsClub/SportsTeam)
    if seo.struct_org_phone:
        contact_point = {
            "@type": "ContactPoint",
            "telephone": seo.struct_org_phone,
            "contactType": "customer service",
        }
        
        # Orari disponibilità (hoursAvailable dentro ContactPoint)
        if seo.struct_org_hours:
            hours_list = []
            for spec in seo.struct_org_hours:
                if hasattr(spec, 'value') and hasattr(spec.value, 'struct_dict'):
                    hour_data = spec.value.struct_dict.copy()
                    # Converti datetime.time in stringhe "HH:MM"
                    if 'opens' in hour_data and hasattr(hour_data['opens'], 'strftime'):
                        hour_data['opens'] = hour_data['opens'].strftime('%H:%M')
                    if 'closes' in hour_data and hasattr(hour_data['closes'], 'strftime'):
                        hour_data['closes'] = hour_data['closes'].strftime('%H:%M')
                    hours_list.append(hour_data)
            if hours_list:
                contact_point["hoursAvailable"] = hours_list
        
        org_data["contactPoint"] = contact_point
    
    # Telefono anche a root level per compatibilità
    if seo.struct_org_phone:
        org_data["telephone"] = seo.struct_org_phone
    
    # Sport e federazione (da SiteSettings)
    try:
        from apps.website.models import SiteSettings
        site_settings = SiteSettings.for_site(site)
        if site_settings.sport:
            org_data["sport"] = site_settings.sport
        if site_settings.member_of_name:
            org_data["memberOf"] = {
                "@type": "SportsOrganization",
                "name": site_settings.member_of_name,
            }
    except Exception:
        pass
    
    # URL social (sameAs)
    if include_social:
        same_as = get_social_urls(page)
        if same_as:
            org_data["sameAs"] = same_as
    
    return org_data


# ============================================================================
# JSON-LD MIXIN
# ============================================================================

class JsonLdMixin:
    """
    Mixin per pagine che generano JSON-LD personalizzato.
    
    Da usare per tipi schema.org NON gestiti automaticamente da wagtailseo:
    - Event, EventSeries
    - ItemList, ImageGallery
    - AboutPage, ContactPage
    - BreadcrumbList
    
    wagtailseo già gestisce automaticamente:
    - Organization (da SeoSettings)
    - Article (per pagine con SeoMixin)
    
    Usage:
    ------
    class EventPage(JsonLdMixin, Page):
        def get_json_ld_type(self):
            return "Event"
        
        def get_json_ld_data(self, request=None):
            return {
                "name": self.title,
                "startDate": self.date.isoformat(),
            }
    
    Nel template Jinja2:
    {% if page.get_json_ld is defined %}
    <script type="application/ld+json">{{ page.get_json_ld() }}</script>
    {% endif %}
    """
    
    def get_json_ld_type(self) -> str:
        """
        Ritorna il tipo schema.org primario.
        
        Returns:
            String con il tipo schema.org
        """
        raise NotImplementedError("Subclass must implement get_json_ld_type()")
    
    def get_json_ld_data(self, request=None) -> dict[str, Any]:
        """
        Ritorna i dati per il JSON-LD.
        
        Args:
            request: HttpRequest opzionale per generare URL assoluti
            
        Returns:
            Dict con i dati da inserire nel JSON-LD
        """
        raise NotImplementedError("Subclass must implement get_json_ld_data()")
    
    def get_json_ld(self, request=None) -> str:
        """
        Genera il JSON-LD completo pronto per l'inserimento nel template.
        
        Args:
            request: HttpRequest opzionale
            
        Returns:
            String JSON-LD (safe per template)
        """
        try:
            data = {
                "@context": "https://schema.org",
                "@type": self.get_json_ld_type(),
                **self.get_json_ld_data(request),
            }
            return mark_safe(json.dumps(data, cls=SchemaEncoder, ensure_ascii=False, indent=2))
        except Exception as e:
            # In caso di errore, ritorna JSON vuoto invece di rompere la pagina
            return mark_safe('{}')


# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================

# Alias per compatibilità con codice esistente
SchemaOrgMixin = JsonLdMixin


# ============================================================================
# SCHEMA.ORG HELPER FUNCTIONS
# ============================================================================

def postal_address(
    street: str = "",
    city: str = "",
    region: str = "",
    country: str = "IT",
    postal_code: str = "",
) -> dict:
    """
    Genera oggetto PostalAddress schema.org.
    https://schema.org/PostalAddress
    """
    address = {"@type": "PostalAddress"}
    if street:
        address["streetAddress"] = street
    if city:
        address["addressLocality"] = city
    if region:
        address["addressRegion"] = region
    if postal_code:
        address["postalCode"] = postal_code
    if country:
        address["addressCountry"] = country
    return address


def geo_coordinates(lat: float, lon: float) -> dict:
    """
    Genera oggetto GeoCoordinates schema.org.
    https://schema.org/GeoCoordinates
    """
    return {
        "@type": "GeoCoordinates",
        "latitude": lat,
        "longitude": lon,
    }


def place(
    name: str,
    street: str = "",
    city: str = "",
    region: str = "",
    country: str = "IT",
    postal_code: str = "",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> dict:
    """
    Genera oggetto Place schema.org.
    https://schema.org/Place
    """
    p = {"@type": "Place", "name": name}
    
    if street or city or region:
        p["address"] = postal_address(street, city, region, country, postal_code)
    
    if lat is not None and lon is not None:
        p["geo"] = geo_coordinates(lat, lon)
    
    return p


def contact_point(
    telephone: str = "",
    email: str = "",
    contact_type: str = "customer service",
    available_languages: Optional[list] = None,
) -> dict:
    """
    Genera oggetto ContactPoint schema.org.
    https://schema.org/ContactPoint
    """
    cp = {"@type": "ContactPoint", "contactType": contact_type}
    
    if telephone:
        cp["telephone"] = telephone
    if email:
        cp["email"] = email
    if available_languages:
        cp["availableLanguage"] = available_languages
    
    return cp


def event(
    name: str,
    start_date: Union[str, datetime, date],
    end_date: Union[str, datetime, date, None] = None,
    description: str = "",
    location: Optional[dict] = None,
    organizer: Optional[dict] = None,
    image_url: str = "",
    url: str = "",
    event_status: str = "EventScheduled",
    event_attendance_mode: str = "OfflineEventAttendanceMode",
) -> dict:
    """
    Genera oggetto Event schema.org completo.
    https://schema.org/Event
    
    Args:
        name: Nome evento
        start_date: Data/ora inizio (ISO 8601)
        end_date: Data/ora fine opzionale
        description: Descrizione (verrà pulita da HTML)
        location: Dict Place schema.org
        organizer: Dict Organization schema.org
        image_url: URL immagine evento
        url: URL pagina evento
        event_status: EventScheduled|EventCancelled|EventPostponed|EventRescheduled
        event_attendance_mode: Online|Offline|Mixed EventAttendanceMode
        
    Returns:
        Dict Event schema.org
    """
    # Converti date in stringhe ISO
    if isinstance(start_date, (datetime, date)):
        start_date = start_date.isoformat()
    
    e = {
        "@type": "Event",
        "name": name,
        "startDate": start_date,
        "eventStatus": f"https://schema.org/{event_status}",
        "eventAttendanceMode": f"https://schema.org/{event_attendance_mode}",
    }
    
    if end_date:
        if isinstance(end_date, (datetime, date)):
            end_date = end_date.isoformat()
        e["endDate"] = end_date
    
    if description:
        e["description"] = clean_html(description)
    
    if location:
        e["location"] = location
    
    if organizer:
        e["organizer"] = organizer
    
    if image_url:
        e["image"] = image_url
    
    if url:
        e["url"] = url
    
    return e


def person(
    name: str,
    job_title: str = "",
    image_url: str = "",
    url: str = "",
) -> dict:
    """
    Genera oggetto Person schema.org.
    https://schema.org/Person
    """
    p = {"@type": "Person", "name": name}
    
    if job_title:
        p["jobTitle"] = job_title
    if image_url:
        p["image"] = image_url
    if url:
        p["url"] = url
    
    return p


def image_object(
    url: str,
    width: int = 0,
    height: int = 0,
    caption: str = "",
    name: str = "",
) -> dict:
    """
    Genera oggetto ImageObject schema.org.
    https://schema.org/ImageObject
    """
    obj = {"@type": "ImageObject", "url": url}
    
    if width and height:
        obj["width"] = width
        obj["height"] = height
    if caption:
        obj["caption"] = caption
    if name:
        obj["name"] = name
    
    return obj


def article(
    headline: str,
    image_url: str = "",
    date_published: str = "",
    date_modified: str = "",
    author: Optional[Union[str, dict]] = None,
    article_section: str = "",
    url: str = "",
    description: str = "",
    word_count: int = 0,
) -> dict:
    """
    Genera oggetto Article schema.org.
    https://schema.org/Article
    
    Note:
        Per news e blog, wagtailseo gestisce automaticamente Article structured data.
        Questa funzione è utile per ItemList o casi custom.
    """
    art = {"@type": "Article", "headline": headline}
    
    if image_url:
        art["image"] = image_url
    if date_published:
        art["datePublished"] = date_published
    if date_modified:
        art["dateModified"] = date_modified
    if author:
        if isinstance(author, str):
            art["author"] = {"@type": "Person", "name": author}
        else:
            art["author"] = author
    if article_section:
        art["articleSection"] = article_section
    if url:
        art["url"] = url
    if description:
        art["description"] = clean_html(description)
    if word_count:
        art["wordCount"] = word_count
    
    return art


def item_list(
    name: str,
    description: str = "",
    items: Optional[list] = None,
    url: str = "",
) -> dict:
    """
    Genera oggetto ItemList schema.org.
    https://schema.org/ItemList
    """
    il = {
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(items) if items else 0,
        "itemListElement": items or [],
    }
    
    if description:
        il["description"] = clean_html(description)
    if url:
        il["url"] = url
    
    return il


def list_item(position: int, item: dict) -> dict:
    """
    Genera oggetto ListItem schema.org.
    https://schema.org/ListItem
    """
    return {
        "@type": "ListItem",
        "position": position,
        "item": item,
    }


def breadcrumb_list(items: list) -> dict:
    """
    Genera oggetto BreadcrumbList schema.org.
    https://schema.org/BreadcrumbList
    
    Args:
        items: Lista di tuple (name, url)
        
    Example:
        breadcrumb_list([
            ("Home", "https://example.com/"),
            ("Eventi", "https://example.com/eventi/"),
            ("Rally 2024", "https://example.com/eventi/rally-2024/"),
        ])
    """
    elements = []
    for i, (name, url) in enumerate(items, 1):
        elements.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": url,
        })
    
    return {
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def web_page(
    name: str,
    description: str = "",
    url: str = "",
    image_url: str = "",
    page_type: str = "WebPage",
) -> dict:
    """
    Genera oggetto WebPage schema.org (o sottotipi).
    https://schema.org/WebPage
    
    Args:
        page_type: WebPage|AboutPage|ContactPage|FAQPage|etc.
    """
    wp = {"@type": page_type, "name": name}
    
    if description:
        wp["description"] = clean_html(description)
    if url:
        wp["url"] = url
    if image_url:
        wp["image"] = image_url
    
    return wp


def sports_organization(
    name: str,
    founding_date: Optional[Union[str, date]] = None,
    member_of: Optional[str] = None,
    sport: str = "Motorcycling",
    **kwargs,
) -> dict:
    """
    Genera oggetto SportsOrganization/SportsClub schema.org.
    https://schema.org/SportsOrganization
    
    Specifico per club sportivi come motoclub.
    """
    org = {"@type": "SportsClub", "name": name, "sport": sport}
    
    if founding_date:
        if isinstance(founding_date, date):
            founding_date = founding_date.isoformat()
        org["foundingDate"] = founding_date
    
    if member_of:
        org["memberOf"] = {"@type": "SportsOrganization", "name": member_of}
    
    # Merge altri kwargs
    org.update(kwargs)
    
    return org


# ============================================================================
# MULTILINGUAL HELPERS
# ============================================================================

def get_page_url_for_locale(page, locale_code: str) -> Optional[str]:
    """
    Ottiene l'URL di una pagina tradotta per una specifica lingua.
    
    Args:
        page: Pagina Wagtail
        locale_code: Codice lingua (es. 'it', 'en')
        
    Returns:
        URL della traduzione o None se non esiste
    """
    try:
        translations = page.get_translations(inclusive=True)
        for trans in translations:
            if trans.locale.language_code == locale_code:
                return trans.full_url
        return None
    except Exception:
        return None


def get_alternate_urls(page) -> dict:
    """
    Ottiene tutti gli URL alternativi per hreflang.
    
    Args:
        page: Pagina Wagtail
        
    Returns:
        Dict {locale_code: url} per tutte le traduzioni
    """
    urls = {}
    try:
        translations = page.get_translations(inclusive=True)
        for trans in translations:
            urls[trans.locale.language_code] = trans.full_url
    except Exception:
        pass
    return urls
