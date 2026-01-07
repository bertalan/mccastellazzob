#!/bin/bash
# ============================================
# Script di Deploy per mccastellazzob.com
# ============================================
# Server di produzione con BT Panel (aaPanel)
# Stack: Python 3.12, Gunicorn, Nginx, PostgreSQL
# ============================================

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurazione
PROJECT_DIR="/www/wwwroot/mccastellazzob.com"
VENV_DIR="${PROJECT_DIR}/venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"
GUNICORN_SOCKET="${PROJECT_DIR}/mccastellazzob/mccastellazzob.sock"
SUPERVISOR_CONF="mccastellazzob"
BRANCH="${1:-main}"

# Banner
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   mccastellazzob.com - Deploy Script     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Funzione per logging
log_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Verifica utente root
if [[ $EUID -ne 0 ]]; then
   log_error "Questo script deve essere eseguito come root"
fi

# Verifica directory progetto
if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Directory progetto non trovata: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# 1. Backup del database
log_info "Creazione backup database..."
BACKUP_FILE="${PROJECT_DIR}/backups/mccastellazzob_$(date +%Y-%m-%d_%H-%M-%S).sql.gz"
mkdir -p "${PROJECT_DIR}/backups"
if sudo -u postgres pg_dump mccastellazzob | gzip > "$BACKUP_FILE"; then
    log_success "Backup creato: $BACKUP_FILE"
else
    log_error "Fallito backup database"
fi

# 2. Pull dal repository
log_info "Pull dal repository (branch: $BRANCH)..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"
log_success "Codice aggiornato"

# 3. Attiva virtual environment e aggiorna dipendenze
log_info "Attivazione virtual environment..."
if [[ ! -d "$VENV_DIR" ]]; then
    log_info "Creazione nuovo virtual environment..."
    python3.12 -m venv "$VENV_DIR"
fi
source "${VENV_DIR}/bin/activate"
log_success "Virtual environment attivato"

log_info "Aggiornamento dipendenze Python..."
$PIP install --upgrade pip
$PIP install -e "." --no-deps
log_success "Dipendenze aggiornate"

# 4. Audit sicurezza (opzionale, non blocca il deploy)
log_info "Esecuzione audit sicurezza..."
if $PIP show pip-audit > /dev/null 2>&1; then
    $PIP install pip-audit
fi
${VENV_DIR}/bin/pip-audit --ignore-vuln PYSEC-2022-42969 || echo -e "${YELLOW}⚠ Audit con warning, verifica manualmente${NC}"

# 5. Migrazioni database
log_info "Esecuzione migrazioni database..."
export DJANGO_SETTINGS_MODULE="mccastellazzob.settings.prod"
$PYTHON manage.py migrate --noinput
log_success "Migrazioni completate"

# 6. Raccolta file statici
log_info "Raccolta file statici..."
$PYTHON manage.py collectstatic --noinput --clear
log_success "File statici raccolti"

# 7. Compilazione traduzioni
log_info "Compilazione file di traduzione..."
if [[ -d "${PROJECT_DIR}/locale" ]]; then
    $PYTHON manage.py compilemessages
    log_success "Traduzioni compilate"
else
    echo -e "${YELLOW}⚠ Directory locale non trovata, skip compilemessages${NC}"
fi

# 8. Riavvio Gunicorn via Supervisor
log_info "Riavvio servizio Gunicorn..."
if supervisorctl status "$SUPERVISOR_CONF" > /dev/null 2>&1; then
    supervisorctl restart "$SUPERVISOR_CONF"
    log_success "Gunicorn riavviato via Supervisor"
elif systemctl is-active --quiet gunicorn; then
    systemctl restart gunicorn
    log_success "Gunicorn riavviato via systemd"
else
    # Riavvio manuale cercando il processo
    pkill -f "gunicorn.*mccastellazzob" || true
    sleep 2
    cd "${PROJECT_DIR}"
    ${VENV_DIR}/bin/gunicorn \
        --bind unix:${GUNICORN_SOCKET} \
        --workers 3 \
        --timeout 120 \
        --user www \
        --group www \
        --daemon \
        mccastellazzob.wsgi:application
    log_success "Gunicorn avviato manualmente"
fi

# 9. Ricarica Nginx
log_info "Ricarica configurazione Nginx..."
nginx -t && nginx -s reload
log_success "Nginx ricaricato"

# 10. Verifica stato
log_info "Verifica stato servizi..."
echo ""

# Verifica socket Gunicorn
if [[ -S "$GUNICORN_SOCKET" ]]; then
    echo -e "  Gunicorn Socket: ${GREEN}OK${NC}"
else
    echo -e "  Gunicorn Socket: ${RED}NON TROVATO${NC}"
fi

# Verifica processo Gunicorn
if pgrep -f "gunicorn.*mccastellazzob" > /dev/null; then
    echo -e "  Gunicorn Process: ${GREEN}OK${NC}"
else
    echo -e "  Gunicorn Process: ${RED}NON ATTIVO${NC}"
fi

# Verifica Nginx
if systemctl is-active --quiet nginx; then
    echo -e "  Nginx: ${GREEN}OK${NC}"
else
    echo -e "  Nginx: ${RED}NON ATTIVO${NC}"
fi

# Verifica PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo -e "  PostgreSQL: ${GREEN}OK${NC}"
else
    echo -e "  PostgreSQL: ${RED}NON ATTIVO${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}   Deploy completato con successo!         ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Backup: ${BACKUP_FILE}"
echo -e "Branch: ${BRANCH}"
echo -e "Data: $(date)"
echo ""

# Pulizia backup vecchi (mantieni ultimi 7)
log_info "Pulizia backup vecchi (mantiene ultimi 7)..."
ls -t "${PROJECT_DIR}/backups/"*.sql.gz 2>/dev/null | tail -n +8 | xargs -r rm
log_success "Pulizia completata"
