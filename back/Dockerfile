FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
		PYTHONUNBUFFERED=1 \
		PIP_NO_CACHE_DIR=1

# Dépendances système requises par WeasyPrint (cairo/pango/gdk-pixbuf) et polices
RUN apt-get update && apt-get install -y --no-install-recommends \
		libcairo2 \
		libpango-1.0-0 \
		libpangocairo-1.0-0 \
		libpangoft2-1.0-0 \
		libgdk-pixbuf-2.0-0 \
		libffi8 \
		shared-mime-info \
		fonts-dejavu \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "EuropGreenSolar.wsgi:application", "--bind", "0.0.0.0:8000"]
