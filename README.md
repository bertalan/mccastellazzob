# mccastellazzob.com - Moto Club Castellazzo Bormida

[![CI](https://github.com/bertalan/mccastellazzob/actions/workflows/ci.yml/badge.svg)](https://github.com/bertalan/mccastellazzob/actions/workflows/ci.yml)

Sito web del Moto Club Castellazzo Bormida, sviluppato con [CodeRedCMS](https://www.coderedcorp.com/cms/) (Wagtail/Django).

> ⚠️ **Nota**: Docker è utilizzato **solo per lo sviluppo locale**. In produzione il sito gira direttamente su server con nginx + gunicorn.

## Stack Tecnologico

- **Python** 3.12
- **Django** 5.2 LTS
- **Wagtail** 7.0 LTS
- **CodeRedCMS** 6.0.0
- **PostgreSQL** 15

## 🎨 Colori del Brand

- **Giallo Dorato**: `#D4AF37` (oro)
- **Carminio**: `#960018` (rosso scuro)

## 🌐 Multilingua

Il sito supporta **3 lingue**:
- 🇮🇹 **Italiano** (default, senza prefisso URL)
- 🇬🇧 **English** (`/en/`)
- 🇫🇷 **Français** (`/fr/`)

Vedi [docs/MULTILINGUA.md](docs/MULTILINGUA.md) per la documentazione completa.

## 📁 Struttura del Progetto

```
mccastellazzob.com/
├── apps/
│   ├── core/           # Mixin condivisi, validators, schema.org
│   ├── media/          # CustomImage, CustomDocument
│   ├── users/          # Modello User con email auth
│   └── website/        # Pagine, snippet, blocks, views
├── mccastellazzob/
│   ├── settings/       # Settings Django (base, dev, prod, test, docker)
│   ├── urls.py
│   └── wsgi.py
├── tests/
│   └── factories/      # Factory classes per TDD
├── docker/             # Configurazioni Docker (solo sviluppo)
├── docs/               # Documentazione
├── brief/              # Backup e file originali
├── pyproject.toml      # Configurazione unificata progetto
├── deploy.sh           # Script deploy produzione
└── manage.py
```

## 🚀 Quick Start

### Con Docker (raccomandato per sviluppo)

```bash
# Clona il repository
git clone https://github.com/bertalan/mccastellazzob.git
cd mccastellazzob

# Copia il file di configurazione
cp .env.example .env

# Costruisci e avvia i servizi
docker compose up -d

# Il sito sarà disponibile su http://localhost:8000
```

### Senza Docker

```bash
# Crea virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -e ".[dev]"

# Configura database (PostgreSQL locale)
export DJANGO_SETTINGS_MODULE=mccastellazzob.settings.dev
python manage.py migrate
python manage.py createsuperuser

# Avvia server di sviluppo
python manage.py runserver
```

## 🧪 Testing

```bash
# Esegui tutti i test
pytest

# Con coverage
pytest --cov=apps --cov-report=html

# Solo test specifici
pytest tests/test_users.py -v
```

## 🔍 Code Quality

```bash
# Pre-commit hooks (configurazione automatica)
pre-commit install

# Esecuzione manuale
pre-commit run --all-files

# Singoli tool
ruff check .
ruff format .
mypy apps
bandit -r apps -c pyproject.toml
pip-audit
```

## 📦 Deploy Produzione

**In produzione NON si usa Docker.** Il sito gira su server con BT Panel (nginx + gunicorn + PostgreSQL).

```bash
# SSH nel server
ssh root@server

# Esegui lo script di deploy
cd /www/wwwroot/mccastellazzob.com
./deploy.sh main
```

Lo script `deploy.sh`:
1. Crea backup del database
2. Pull dal repository Git
3. Aggiorna dipendenze Python
4. Esegue audit sicurezza
5. Applica migrazioni database
6. Raccoglie file statici
7. Compila traduzioni
8. Riavvia Gunicorn
9. Ricarica Nginx

## 🐛 Troubleshooting

### Container non parte
```bash
docker compose logs web
```

### Database non accessibile
```bash
docker compose logs db
docker compose exec db psql -U mccastellazzob -d mccastellazzob
```

### File statici non trovati
```bash
docker compose exec web python manage.py collectstatic --noinput
```

## 📜 Licenza

Tutti i diritti riservati © Moto Club Castellazzo Bormida

---

**Moto Club Castellazzo Bormida** - © 2026
