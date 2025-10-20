# ⚡ Quick Start - Développeurs

## 🐳 Avec Docker (Recommandé)

```bash
# 1. Cloner
git clone https://github.com/Gatyd/EuropGreen-Solar.git
cd EuropGreen-Solar

# 2. Configurer
cp .env.example .env
# Garder les valeurs par défaut pour le dev local

# 3. Lancer
docker compose up -d

# 4. Créer un superuser
docker compose exec backend python manage.py createsuperuser

# 5. Accéder
# Frontend: http://localhost
# Admin: http://localhost/admin/
# API Docs: http://localhost/api/docs/
```

## 💻 Sans Docker (Développement manuel)

### Backend

```bash
cd back
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer
python manage.py runserver  # http://localhost:8000
```

### Frontend

```bash
cd front
npm install
npm run dev  # http://localhost:3000
```

### Redis & Celery (optionnel pour dev)

```bash
# Terminal 1: Redis
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Celery Worker
cd back
celery -A EuropGreenSolar worker -l info

# Terminal 3: Celery Beat
celery -A EuropGreenSolar beat -l info
```

---

## 🧪 Tests

```bash
# Backend
cd back
python manage.py test

# Frontend
cd front
npm run test
```

---

## 📝 Conventions de Code

- **Backend** : PEP 8 (Python)
- **Frontend** : ESLint + Prettier
- **Commits** : Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

---

## 🔧 Variables d'Environnement Locales

Pour le développement local, gardez les valeurs par défaut de `.env.example` :
- `DEBUG=True`
- `PROXY_URL=http://localhost:8000`
- `DB_HOST=localhost` (si sans Docker)
