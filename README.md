# MC Castellazzo Bormida - Sito Motoclub

Sito web ufficiale del Motoclub Castellazzo Bormida, costruito con **CodeRedCMS 6.x / Wagtail 7.x LTS / Django 5.2 LTS**.

## 🏍️ Caratteristiche

- **5 lingue**: IT (default), EN, FR, DE, ES - tutte paritarie con traduzioni complete
- **Schema.org**: JSON-LD automatico via `JsonLdMixin` (SportsClub, Event, AboutPage...)
- **SEO**: Fonte unica dati in `wagtailseo.SeoSettings`, hreflang multilingua
- **Tema**: Oro #D4AF37, Blu #1B263B, Amaranto #9B1D64 (Tailwind CSS)
- **Mappe**: OpenStreetMap + Leaflet.js + Nominatim (no Google)
- **Geocoding**: Autocompletamento indirizzi con coordinate automatiche
- **Auth**: Frontend authentication con django-allauth
- **TDD**: Test-driven development con pytest
- **WCAG 2.2 AAA**: Accessibilità avanzata (focus visible, aria-labels, contrasto)

## 📄 Pagine e Schema.org

| Pagina | Tipo schema.org | Modello |
|--------|-----------------|---------|
| Homepage | SportsClub | `HomePage` |
| Articoli (indice) | ItemList | `NewsIndexPage` |
| Articolo singolo | NewsArticle | `NewsPage` |
| Eventi Anno | EventSeries | `EventsPage` |
| Dettaglio Evento | Event | `EventDetailPage` |
| Archivio Eventi | ItemList | `EventsArchivePage` |
| Chi Siamo | AboutPage | `AboutPage` |
| Consiglio | Organization | `BoardPage` |
| Trasparenza | WebPage | `TransparencyPage` |
| Contatti | Organization | `ContactPage` |
| Galleria | ImageGallery | `GalleryPage` |
| Timeline | ItemList | `TimelinePage` |
| Privacy | WebPage | `PrivacyPage` |

## 🚀 Sviluppo con Docker

```bash
# Avvia l'ambiente di sviluppo
docker compose up -d

# Frontend: http://localhost:8000
# Admin: http://localhost:8000/admin/

# Credenziali default:
# Username: admin
# Password: admin123
```

## 📁 Struttura Progetto

```
mccastellazzob/
├── apps/
│   ├── core/           # SEO (JsonLdMixin), API metadati, geocoding, traduzioni
│   ├── website/        # Models (News, Eventi, Galleria), blocks, snippets
│   └── custom_user/    # User model personalizzato
├── mccastellazzob/     # Settings Django (base, dev, docker, prod)
├── templates/          # Jinja2 templates (.jinja2)
├── static/js/          # Scripts (address_geocoding.js, gallery_image_metadata.js)
├── locale/             # Traduzioni .po/.mo (de, en, es, fr)
└── tests/              # Test suite TDD (pytest)
```

## 📰 Sistema News/Blog

Il sistema articoli (`NewsIndexPage` + `NewsPage`) offre:

- **Ricerca globale**: Cerca in articoli E eventi contemporaneamente
- **Filtro per tag**: Tag condivisi tra articoli ed eventi
- **Pagine in evidenza**: Selezione manuale di pagine da evidenziare
- **Categorie**: Classificazione tramite CodeRedCMS classifiers
- **Galleria immagini**: Con lightbox sfogliabile
- **Tag recenti**: Ordinati per ultima pubblicazione

### API Admin

- `/admin/api/image-metadata/<id>/` - Metadati immagine (titolo, descrizione, tag)

## 🔧 Architettura SEO

Il modulo `apps/core/seo.py` centralizza la gestione SEO:

- **Fonte unica**: `wagtailseo.SeoSettings` (Settings > SEO in admin)
- **`SiteSettings`**: Solo social URLs e footer (no dati org duplicati)
- **`JsonLdMixin`**: Mixin per JSON-LD custom nelle pagine
- **Helpers**: `get_organization_data()`, `place()`, `event()`, `person()`, `clean_html()`
- **Multilingua**: `get_alternate_urls()`, hreflang automatici in base.jinja2

## 🔧 Comandi Docker

```bash
# Migrazioni
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Superuser
docker compose exec web python manage.py createsuperuser

# Collectstatic
docker compose exec web python manage.py collectstatic --noinput

# Test
docker compose exec web pytest

# Compilare traduzioni
docker compose exec web python manage.py compilemessages
```

## 🌐 Internazionalizzazione

Le traduzioni sono gestite su due livelli:

1. **UI (file .po)**: Template strings in `locale/{lang}/LC_MESSAGES/django.po`
2. **Contenuti DB**: Pagine Wagtail tradotte con wagtail-localize

### URL tradotti
- `/it/articoli/` → `/en/articles/` → `/fr/articles/` → `/de/artikel/` → `/es/articulos/`
- `/it/galleria/` → `/en/gallery/` → `/fr/galerie/` → `/de/galerie/` → `/es/galeria/`
- `/it/eventi/` → `/en/events/` → `/fr/evenements/` → `/de/veranstaltungen/` → `/es/eventos/`

### Forzare Traduzioni

Il comando `force_translate` sincronizza e traduce automaticamente le pagine:

```bash
# Tradurre UNA pagina specifica (per ID)
docker compose exec web python manage.py force_translate --page=3

# Tradurre UNA pagina specifica (per slug)
docker compose exec web python manage.py force_translate --slug=home

# Solo vedere cosa farebbe (dry-run)
docker compose exec web python manage.py force_translate --page=5 --dry-run

# Tradurre TUTTE le pagine
docker compose exec web python manage.py force_translate

# Saltare segmenti già tradotti (più veloce)
docker compose exec web python manage.py force_translate --skip-existing
```

| Pagina | ID |
|--------|-----|
| Home | 3 |
| Articoli | 4 |
| Chi Siamo | 5 |
| Consiglio | 6 |
| Trasparenza | 7 |
| Motocavalcata | 15 |
| Galleria | 1761 |

## 🧪 Test

```bash
# Tutti i test
docker compose exec web pytest

# Solo traduzioni
docker compose exec web pytest tests/test_translations.py -v

# Coverage
docker compose exec web pytest --cov=apps
```

## 📦 Tech Stack

- **Framework**: Django 5.2 LTS + Wagtail 7.x LTS + CodeRedCMS 6.x
- **Database**: PostgreSQL 15
- **Template Engine**: Jinja2 (.jinja2)
- **CSS**: Tailwind CSS con palette custom (gold, navy, amaranth)
- **SEO**: wagtailseo (SeoSettings, struct_org_*)
- **i18n**: wagtail-localize + django i18n
- **Auth**: django-allauth
- **Testing**: pytest + pytest-django + factory_boy
- **Python**: 3.11+

## ♿ Accessibilità (WCAG 2.2 AAA)

Il sito rispetta le linee guida WCAG 2.2 livello AAA:

- **Focus visible**: `ring-2 ring-gold ring-offset-2` su tutti i link interattivi
- **Contrasto**: Testo `gray-700` su sfondo chiaro (rapporto 7:1)
- **Aria-labels**: Contesto completo per screen readers
- **Role search**: Form di ricerca con ruolo semantico
- **Aria-live**: Messaggi dinamici annunciati agli screen readers
- **Skip links**: Salta al contenuto principale
- **Datetime semantico**: Elementi `<time>` con attributo `datetime`

## 📚 Documentazione

- **[CLAUDE.md](CLAUDE.md)**: Istruzioni sviluppo e principi chiave
- **[SEO_SCHEMA_GUIDE.md](SEO_SCHEMA_GUIDE.md)**: Guida SEO e schema.org
- **[MULTILANGUAGE_FLAGS_GUIDE.md](MULTILANGUAGE_FLAGS_GUIDE.md)**: Gestione multilingua
- **[TDD_NAVIGATION_REPORT.md](TDD_NAVIGATION_REPORT.md)**: Report navigazione

## 📝 License

MIT License - MC Castellazzo Bormida
