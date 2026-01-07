# ============================================
# Dockerfile per mccastellazzob.com
# SOLO PER SVILUPPO LOCALE
# ============================================
# In produzione NON si usa Docker!
# Django/Wagtail/CodeRedCMS con Python 3.12
# ============================================
FROM python:3.12-slim-bookworm

# Variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia pyproject.toml e installa dipendenze Python
COPY pyproject.toml /app/pyproject.toml

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]" && \
    pip install --no-cache-dir gunicorn psycopg2-binary pillow-heif

# Copia il codice dell'applicazione
COPY manage.py /app/manage.py
COPY mccastellazzob /app/mccastellazzob
COPY apps /app/apps
COPY tests /app/tests
COPY conftest.py /app/conftest.py

# Crea directory per static e media
RUN mkdir -p /app/static /app/media

# Script di entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Esponi la porta
EXPOSE 8000

# Imposta l'entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Comando di default
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "mccastellazzob.wsgi:application"]
