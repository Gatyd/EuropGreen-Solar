FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt \
	&& python -m playwright install --with-deps chromium

COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "EuropGreenSolar.wsgi:application", "--bind", "0.0.0.0:8000"]
