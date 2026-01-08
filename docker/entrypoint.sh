#!/bin/bash
set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   mccastellazzob.com - Docker Start   ${NC}"
echo -e "${GREEN}========================================${NC}"

# Imposta il modulo settings Django
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mccastellazzob.settings.docker}"

echo -e "${YELLOW}→ Usando settings: ${DJANGO_SETTINGS_MODULE}${NC}"

# Attendi che il database sia pronto
echo -e "${YELLOW}→ Attendo che PostgreSQL sia disponibile...${NC}"
until python -c "
import os
import psycopg2
conn = psycopg2.connect(
    dbname=os.environ.get('POSTGRES_DB', 'mccastellazzob'),
    user=os.environ.get('POSTGRES_USER', 'mccastellazzob'),
    password=os.environ.get('POSTGRES_PASSWORD', ''),
    host=os.environ.get('POSTGRES_HOST', 'db'),
    port=os.environ.get('POSTGRES_PORT', '5432')
)
conn.close()
" 2>/dev/null; do
    echo -e "${YELLOW}   PostgreSQL non ancora pronto, riprovo in 2 secondi...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL è pronto!${NC}"

# Esegui le migrazioni del database
echo -e "${YELLOW}→ Esecuzione migrazioni database...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrazioni completate!${NC}"

# Raccogli i file statici
echo -e "${YELLOW}→ Raccolta file statici...${NC}"
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✓ File statici raccolti!${NC}"

# Compila i file SCSS (se presenti)
if python -c "import sass" 2>/dev/null; then
    echo -e "${YELLOW}→ Compilazione SCSS...${NC}"
    python manage.py compilescss 2>/dev/null || echo -e "${YELLOW}   (compilescss non disponibile, skip)${NC}"
fi

# Crea il superuser se non esiste (solo in dev)
if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    echo -e "${YELLOW}→ Verifica/creazione superuser...${NC}"
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '${SUPERUSER_EMAIL:-admin@mccastellazzob.com}'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password='${SUPERUSER_PASSWORD:-admin123}'
    )
    print('Superuser creato!')
else:
    print('Superuser già esistente.')
"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Avvio applicazione...               ${NC}"
echo -e "${GREEN}========================================${NC}"

# Esegui il comando passato (default: gunicorn)
exec "$@"
