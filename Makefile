# ==================================================
# mccastellazzob.com - Makefile SVILUPPO LOCALE
# ==================================================
# Docker è usato SOLO per lo sviluppo locale!
# In produzione si usa nginx + gunicorn direttamente.
# ==================================================

.PHONY: help build up down logs shell migrate collectstatic createsuperuser clean rebuild db-restore

# Mostra l'aiuto
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║     mccastellazzob.com - Sviluppo Locale con Docker          ║"
	@echo "║     (In produzione NON si usa Docker)                        ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║  make build      - Costruisce le immagini Docker             ║"
	@echo "║  make up         - Avvia tutti i servizi                     ║"
	@echo "║  make down       - Ferma tutti i servizi                     ║"
	@echo "║  make logs       - Mostra i log di tutti i servizi           ║"
	@echo "║  make shell      - Apre una shell nel container web          ║"
	@echo "║  make migrate    - Esegue le migrazioni Django               ║"
	@echo "║  make collectstatic - Raccoglie i file statici               ║"
	@echo "║  make createsuperuser - Crea un superuser                    ║"
	@echo "║  make db-restore - Ripristina il database dal backup         ║"
	@echo "║  make clean      - Rimuove container, immagini e volumi      ║"
	@echo "║  make rebuild    - Ricostruisce tutto da zero                ║"
	@echo "║  make dev        - Avvia in modalità sviluppo                ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""

# Costruisce le immagini Docker
build:
	docker compose build

# Avvia tutti i servizi
up:
	docker compose up -d

# Avvia in modalità sviluppo (con log visibili)
dev:
	docker compose up

# Ferma tutti i servizi
down:
	docker compose down

# Mostra i log
logs:
	docker compose logs -f

# Log di un servizio specifico
logs-web:
	docker compose logs -f web

logs-db:
	docker compose logs -f db

logs-nginx:
	docker compose logs -f nginx

# Apre una shell nel container web
shell:
	docker compose exec web bash

# Shell Django
django-shell:
	docker compose exec web python manage.py shell

# Esegue le migrazioni
migrate:
	docker compose exec web python manage.py migrate

# Crea nuove migrazioni
makemigrations:
	docker compose exec web python manage.py makemigrations

# Raccoglie i file statici
collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

# Crea un superuser
createsuperuser:
	docker compose exec web python manage.py createsuperuser

# Ripristina il database dal backup
db-restore:
	@echo "Ripristino database dal backup..."
	docker compose exec -T db bash -c 'gunzip -c /docker-entrypoint-initdb.d/backup.sql.gz | psql -U $$POSTGRES_USER -d $$POSTGRES_DB'
	@echo "Database ripristinato!"

# Backup del database
db-backup:
	@echo "Creazione backup database..."
	docker compose exec db pg_dump -U $${POSTGRES_USER:-mccastellazzob} $${POSTGRES_DB:-mccastellazzob} | gzip > backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup creato!"

# Pulizia completa
clean:
	docker compose down -v --rmi all --remove-orphans
	@echo "Pulizia completata!"

# Ricostruzione completa
rebuild: clean build up
	@echo "Ricostruzione completata!"

# Verifica stato servizi
status:
	docker compose ps

# Riavvia un servizio
restart-web:
	docker compose restart web

restart-nginx:
	docker compose restart nginx

restart-db:
	docker compose restart db

# Inizializzazione completa (prima volta)
init:
	@echo "Inizializzazione ambiente mccastellazzob.com..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "File .env creato. Modifica i valori prima di continuare."; fi
	@echo "Esegui 'make build' e poi 'make up' per avviare."
