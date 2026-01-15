"""
MC Castellazzo - Schema.org Helpers
====================================
Generazione automatica JSON-LD per schema.org types.
"""
import json
from typing import Any

from django.utils.safestring import mark_safe


class SchemaOrgMixin:
    """
    Mixin per pagine che devono generare JSON-LD schema.org.
    Ogni pagina deve implementare `get_schema_org_type()` e `get_schema_org_data()`.
    """
    
    def get_schema_org_type(self) -> str:
        """Ritorna il tipo schema.org (es. 'Organization', 'Event')."""
        raise NotImplementedError("Subclass must implement get_schema_org_type()")
    
    def get_schema_org_data(self) -> dict[str, Any]:
        """Ritorna i dati per il JSON-LD."""
        raise NotImplementedError("Subclass must implement get_schema_org_data()")
    
    def get_json_ld(self) -> str:
        """Genera il JSON-LD completo."""
        data = {
            "@context": "https://schema.org",
            "@type": self.get_schema_org_type(),
            **self.get_schema_org_data(),
        }
        return mark_safe(json.dumps(data, ensure_ascii=False, indent=2))


def postal_address(
    street: str = "",
    city: str = "Torino",
    region: str = "Piedmont",
    country: str = "IT",
    postal_code: str = "",
) -> dict:
    """
    Genera un oggetto PostalAddress schema.org.
    """
    address = {
        "@type": "PostalAddress",
        "addressLocality": city,
        "addressRegion": region,
        "addressCountry": country,
    }
    if street:
        address["streetAddress"] = street
    if postal_code:
        address["postalCode"] = postal_code
    return address


def contact_point(
    telephone: str = "",
    email: str = "",
    contact_type: str = "customer service",
) -> dict:
    """
    Genera un oggetto ContactPoint schema.org.
    """
    point = {
        "@type": "ContactPoint",
        "contactType": contact_type,
    }
    if telephone:
        point["telephone"] = telephone
    if email:
        point["email"] = email
    return point


def image_object(
    url: str,
    width: int = 0,
    height: int = 0,
    caption: str = "",
) -> dict:
    """
    Genera un oggetto ImageObject schema.org.
    """
    obj = {
        "@type": "ImageObject",
        "url": url,
    }
    if width and height:
        obj["width"] = width
        obj["height"] = height
    if caption:
        obj["caption"] = caption
    return obj


def place(
    name: str,
    street: str = "",
    city: str = "Torino",
    region: str = "Piedmont",
    country: str = "IT",
    lat: float = None,
    lon: float = None,
) -> dict:
    """
    Genera un oggetto Place schema.org.
    """
    p = {
        "@type": "Place",
        "name": name,
        "address": postal_address(street, city, region, country),
    }
    if lat and lon:
        p["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": lat,
            "longitude": lon,
        }
    return p


def article(
    headline: str,
    image_url: str = "",
    date_published: str = "",
    article_section: str = "",
    url: str = "",
    description: str = "",
) -> dict:
    """
    Genera un oggetto Article schema.org.
    """
    art = {
        "@type": "Article",
        "headline": headline,
    }
    if image_url:
        art["image"] = image_url
    if date_published:
        art["datePublished"] = date_published
    if article_section:
        art["articleSection"] = article_section
    if url:
        art["url"] = url
    if description:
        art["description"] = description
    return art


def event(
    name: str,
    start_date: str,
    end_date: str = "",
    location: dict = None,
    image_url: str = "",
    description: str = "",
    organizer: dict = None,
    event_status: str = "EventScheduled",
) -> dict:
    """
    Genera un oggetto Event schema.org.
    """
    e = {
        "@type": "Event",
        "name": name,
        "startDate": start_date,
        "eventStatus": f"https://schema.org/{event_status}",
    }
    if end_date:
        e["endDate"] = end_date
    if location:
        e["location"] = location
    if image_url:
        e["image"] = image_url
    if description:
        e["description"] = description
    if organizer:
        e["organizer"] = organizer
    return e


def person(
    name: str,
    job_title: str = "",
    image_url: str = "",
) -> dict:
    """
    Genera un oggetto Person schema.org.
    """
    p = {
        "@type": "Person",
        "name": name,
    }
    if job_title:
        p["jobTitle"] = job_title
    if image_url:
        p["image"] = image_url
    return p
