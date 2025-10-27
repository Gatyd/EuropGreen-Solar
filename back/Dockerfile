# ============================================================================
# Stage 1: Image de base légère (pour Celery Worker et Beat)
# ============================================================================
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# ============================================================================
# Stage 2: Image avec Playwright (uniquement pour le service Web)
# ============================================================================
FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy AS web

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Installer Playwright UNIQUEMENT pour cette image
RUN python -m playwright install --with-deps chromium

COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "EuropGreenSolar.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug"]
