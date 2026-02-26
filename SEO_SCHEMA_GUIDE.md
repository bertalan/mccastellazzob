# Guida SEO e Schema.org - MC Castellazzo

**Riferimento**: Vedi [CLAUDE.md](CLAUDE.md) per principi sviluppo

## Panoramica Architettura

Il sistema SEO è stato refactorizzato per seguire le best practice di CodeRedCMS/Wagtail e supportare il multilingua (5 lingue: IT, EN, FR, DE, ES).

### Principi Fondamentali

1. **FONTE UNICA**: Tutti i dati organizzazione (nome, indirizzo, telefono, logo) sono in `wagtailseo.SeoSettings`
2. **NO DUPLICATI**: `SiteSettings` contiene solo campi non-SEO (social, footer)
3. **MULTILINGUA**: Template include hreflang per tutte le traduzioni
4. **MODULARITÀ**: `apps.core.seo` fornisce helpers riutilizzabili

---

## Configurazione in Wagtail Admin

### 1. Settings > SEO (wagtailseo.SeoSettings)

Configura qui tutti i dati dell'organizzazione:

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| `struct_org_type` | Tipo schema.org | `SportsClub` |
| `struct_org_name` | Nome organizzazione | `MC Castellazzo Bormida` |
| `struct_org_logo` | Logo (112x112px min) | Immagine |
| `struct_org_image` | Foto organizzazione | Immagine sede |
| `struct_org_phone` | Telefono con prefisso | `+39 335 789 9368` |
| `struct_org_address_street` | Via e numero | `Via S. Francesco, 1` |
| `struct_org_address_locality` | Città | `Castellazzo Bormida` |
| `struct_org_address_region` | Regione/Provincia | `Piemonte` |
| `struct_org_address_postal` | CAP | `15073` |
| `struct_org_address_country` | Paese (ISO) | `IT` |
| `struct_org_geo_lat` | Latitudine | `44.8487` |
| `struct_org_geo_lng` | Longitudine | `8.5756` |
| `struct_org_hours` | Orari apertura | StreamField |

### 2. Settings > Site Settings (SiteSettings)

Solo per campi NON-SEO:

| Campo | Descrizione |
|-------|-------------|
| `logo` | Logo per navbar |
| `favicon` | Favicon browser |
| `facebook_url` | URL pagina Facebook |
| `instagram_url` | URL profilo Instagram |
| `youtube_url` | URL canale YouTube |
| `footer_text` | Testo copyright footer |

---

## Utilizzo nei Modelli

### 1. Import dal modulo SEO

```python
from apps.core.seo import (
    JsonLdMixin,           # Mixin per JSON-LD custom
    clean_html,            # Rimuove HTML da RichTextField
    get_organization_data, # Dati org da SeoSettings
    get_seo_settings,      # Accesso a SeoSettings
    place,                 # Helper Place schema.org
    event,                 # Helper Event schema.org
    person,                # Helper Person schema.org
    breadcrumb_list,       # Helper BreadcrumbList
)
```

### 2. Implementare JSON-LD Custom

```python
class EventDetailPage(JsonLdMixin, Page):
    """Pagina evento - schema.org Event"""
    
    event_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    description = RichTextField(blank=True)
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        """Tipo schema.org principale"""
        return "Event"
    
    def get_json_ld_data(self, request=None) -> dict:
        """Dati per il JSON-LD"""
        return {
            "name": self.event_name,
            "startDate": self.start_date.isoformat(),
            "description": clean_html(self.description),
            "organizer": get_organization_data(self),  # Da SeoSettings
            "url": self.full_url,
        }
```

### 3. Tipi Schema.org Supportati

| Tipo | Pagina | Note |
|------|--------|------|
| `SportsClub` | HomePage | Specifico per motoclub |
| `Event` | EventDetailPage | Dettaglio singolo evento |
| `EventSeries` | EventsPage | Lista eventi anno |
| `ItemList` | EventsArchivePage, GalleryPage | Liste di elementi |
| `AboutPage` | AboutPage | Chi siamo |
| `Organization` | BoardPage, ContactPage | Consiglio, contatti |
| `WebPage` | TransparencyPage | Pagina generica |
| `Article` | News/Blog | Gestito da wagtailseo |

---

## Template Jinja2

### Base Template

Il template `base.jinja2` include automaticamente:

```jinja2
{# Nome organizzazione da SeoSettings #}
<title>{{ page.title }} | {{ settings.wagtailseo.SeoSettings.struct_org_name }}</title>

{# hreflang per SEO multilingua #}
{% for lang_code, lang_url in translations_dict.items() %}
<link rel="alternate" hreflang="{{ lang_code }}" href="{{ lang_url }}" />
{% endfor %}

{# JSON-LD custom dalle pagine #}
{% if page.get_json_ld is defined %}
<script type="application/ld+json">
{{ page.get_json_ld() }}
</script>
{% endif %}

{# JSON-LD Organization da wagtailseo #}
{% if settings.wagtailseo.SeoSettings.struct_meta %}
<script type="application/ld+json">
{{ page.seo_struct_org_json|safe }}
</script>
{% endif %}
```

---

## Helpers Schema.org

### postal_address()

```python
from apps.core.seo import postal_address

addr = postal_address(
    street="Via Roma, 1",
    city="Castellazzo Bormida",
    region="Piemonte",
    postal_code="15073",
    country="IT",
)
# Output: {"@type": "PostalAddress", ...}
```

### place()

```python
from apps.core.seo import place

loc = place(
    name="Circuito Castellazzo",
    street="Via del Circuito, 1",
    city="Castellazzo Bormida",
    lat=44.8487,
    lon=8.5756,
)
# Output: {"@type": "Place", "name": ..., "address": {...}, "geo": {...}}
```

### event()

```python
from apps.core.seo import event, get_organization_data

evt = event(
    name="Rally del Motoclub",
    start_date=self.start_date,
    end_date=self.end_date,
    description="Descrizione evento...",
    location=loc,
    organizer=get_organization_data(self),
    url=self.full_url,
    event_status="EventScheduled",
    event_attendance_mode="OfflineEventAttendanceMode",
)
```

### breadcrumb_list()

```python
from apps.core.seo import breadcrumb_list

breadcrumbs = breadcrumb_list([
    ("Home", "https://mccastellazzo.it/"),
    ("Eventi", "https://mccastellazzo.it/eventi/"),
    ("Rally 2024", "https://mccastellazzo.it/eventi/rally-2024/"),
])
```

---

## Supporto Multilingua

### Ottenere URL Traduzioni

```python
from apps.core.seo import get_alternate_urls, get_page_url_for_locale

# Tutti gli URL tradotti
urls = get_alternate_urls(page)
# {"it": "https://...", "en": "https://...", "fr": "..."}

# URL per lingua specifica
en_url = get_page_url_for_locale(page, "en")
```

### hreflang nel Template

Il template base gestisce automaticamente i tag hreflang:

```html
<link rel="alternate" hreflang="it" href="https://mccastellazzo.it/it/" />
<link rel="alternate" hreflang="en" href="https://mccastellazzo.it/en/" />
<link rel="alternate" hreflang="fr" href="https://mccastellazzo.it/fr/" />
<link rel="alternate" hreflang="de" href="https://mccastellazzo.it/de/" />
<link rel="alternate" hreflang="es" href="https://mccastellazzo.it/es/" />
<link rel="alternate" hreflang="x-default" href="https://mccastellazzo.it/it/" />
```

---

## Migrazione dal Vecchio Sistema

### Prima (DEPRECATO)

```python
from apps.core.schema import SchemaOrgMixin

class MyPage(SchemaOrgMixin, Page):
    def get_schema_org_type(self): 
        return "Event"
    def get_schema_org_data(self): 
        return {...}
```

### Dopo (NUOVO)

```python
from apps.core.seo import JsonLdMixin

class MyPage(JsonLdMixin, Page):
    def get_json_ld_type(self): 
        return "Event"
    def get_json_ld_data(self, request=None): 
        return {...}
```

Il modulo `apps.core.schema` ora è un proxy per retrocompatibilità.

---

## Validazione JSON-LD

Usa questi strumenti per validare il markup:

1. **Google Rich Results Test**: https://search.google.com/test/rich-results
2. **Schema.org Validator**: https://validator.schema.org/
3. **JSON-LD Playground**: https://json-ld.org/playground/

---

## Checklist SEO per Nuove Pagine

- [ ] Usa `JsonLdMixin` per pagine con JSON-LD custom
- [ ] Implementa `get_json_ld_type()` e `get_json_ld_data()`
- [ ] Usa `clean_html()` per RichTextField nelle descrizioni
- [ ] Usa `get_organization_data()` per dati organizzatore
- [ ] Aggiungi `search_description` nel pannello Promote
- [ ] Aggiungi `og_image` per preview social
- [ ] Crea traduzioni per tutte le 5 lingue
