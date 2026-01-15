# ================================
# MC Castellazzo - Dockerfile
# ================================
FROM python:3.11-slim-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    gcc \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# Copy project files
COPY . .

# Create directories for static and media
RUN mkdir -p /app/static /app/media

# Create non-root user
RUN addgroup --system --gid 1001 django && \
    adduser --system --uid 1001 --gid 1001 django && \
    chown -R django:django /app

# Copy and set permissions for entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["gunicorn", "mccastellazzob.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
