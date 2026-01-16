# MC Castellazzo Bormida - Sito Motoclub

Sito web ufficiale del Motoclub Castellazzo Bormida, costruito con **CodeRedCMS/Wagtail** e **Django**.

## 🏍️ Caratteristiche

- **5 lingue**: IT (default), EN, FR, DE, ES - tutte paritarie con traduzioni complete
- **Schema.org**: Markup strutturato per SEO ottimale
- **Tema**: Gradienti oro (#D4AF37) - blu nautico (#1B263B), accenti amaranto (#9B1D64)
- **Mappe**: OpenStreetMap + Nominatim (no Google)
- **Auth**: Frontend authentication con django-allauth

## 📄 Pagine

| Pagina | Descrizione |
|--------|-------------|
| **Home** | Hero carousel, eventi in evidenza, CTA |
| **Novità** | Timeline articoli del club |
| **Chi Siamo** | Storia, valori, statistiche |
| **Consiglio** | Board page con membri |
| **Eventi** | Calendario eventi con archivio |
| **Galleria** | Foto con filtri categoria |
| **Contatti** | Form contatto + mappa |
| **Trasparenza** | Documenti ufficiali |
| **Privacy** | Policy GDPR |

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
│   ├── core/           # Context processors, schema, traduzioni
│   ├── website/        # Models, blocks, snippets (Navbar/Footer)
│   └── custom_user/    # User model personalizzato
├── mccastellazzob/     # Settings Django (base, dev, docker, prod)
├── templates/          # Jinja2 templates (pages, blocks, account)
├── locale/             # Traduzioni .po/.mo (de, en, es, fr)
└── tests/              # Test suite TDD (60+ test)
```

## 🔧 Comandi Utili

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
- `/it/novita/` → `/en/news/` → `/fr/actualites/` → `/de/neuigkeiten/` → `/es/novedades/`
- `/it/galleria/` → `/en/gallery/` → `/fr/galerie/` → `/de/galerie/` → `/es/galeria/`
- `/it/eventi/` → `/en/events/` → `/fr/evenements/` → `/de/veranstaltungen/` → `/es/eventos/`

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

- **Framework**: Django 5.2 + Wagtail 7.0 + CodeRedCMS 6.0
- **Database**: PostgreSQL 15
- **Template Engine**: Jinja2
- **CSS**: Bootstrap 5 con variabili custom
- **i18n**: wagtail-localize 1.9 + django i18n
- **Auth**: django-allauth 65
- **Testing**: pytest 8 + pytest-django + factory_boy
- **Python**: 3.11+

## 📝 License

MIT License - MC Castellazzo Bormida
