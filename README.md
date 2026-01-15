# MC Castellazzo - Sito Motoclub

Sito dinamico per il motoclub MC Castellazzo, costruito con CodeRedCMS/Wagtail.

## Caratteristiche

- **4 lingue**: IT, FR, ES, EN (tutte paritarie)
- **Schema.org**: Tutte le pagine seguono i types schema.org
- **Tema**: Gradienti oro (#D4AF37) - blu nautico (#1B263B), accenti amaranto (#9B1D64)
- **Mappe**: OpenStreetMap + Nominatim (no Google)
- **Auth**: Frontend authentication con django-allauth

## Sviluppo con Docker

```bash
# Avvia l'ambiente di sviluppo
docker compose up -d

# Accedi all'applicazione
# Frontend: http://localhost
# Admin: http://localhost/admin/

# Credenziali default:
# Username: admin
# Password: admin123
```

## Struttura

```
mccastellazzob/
├── apps/
│   ├── core/           # Mixins, validators, schema helpers
│   ├── website/        # Pagine CMS: Home, Timeline, Chi Siamo, Eventi
│   └── custom_user/    # User model personalizzato
├── mccastellazzob/     # Settings Django
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, immagini
└── tests/              # Test TDD
```

## Comandi utili

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
```

## License

MIT License - MC Castellazzo
