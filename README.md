# EuropGreen Solar - Plateforme de Gestion

Application complète de gestion de projets solaires : prospects, devis, installations, facturation.

## 🏗️ Architecture

- **Frontend** : Nuxt 3 + Pinia
- **Backend** : Django 5 + DRF  
- **Proxy** : Nginx
- **Database** : PostgreSQL
- **Cache** : Redis
- **Tasks** : Celery + Beat

## 🚀 Déploiement Production

```bash
# 1. Configurer l'environnement
cp .env.example .env
nano .env  # Modifier selon vos besoins

# 2. Lancer le déploiement
chmod +x deploy.sh
./deploy.sh
```

**📖 Documentation complète de déploiement** : [DEPLOY.md](./DEPLOY.md)

## 🔧 Développement Local

### Backend
```bash
cd back
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```bash
cd front
npm install
npm run dev
```

## 📁 Structure du Projet

```
EuropGreen-Solar/
├── back/               # Django backend + API
├── front/              # Nuxt 3 frontend
├── nginx/              # Configuration Nginx (reverse proxy)
├── docker-compose.yml  # Orchestration complète
├── .env.example        # Template variables d'environnement
├── deploy.sh           # Script de déploiement automatique
└── DEPLOY.md           # Guide complet de déploiement
```

## 🌐 URLs en Production

| Route | Service | Description |
|-------|---------|-------------|
| `/` | Frontend | Interface utilisateur |
| `/api/` | Backend | API REST |
| `/admin/` | Backend | Interface admin Django |
| `/media/` | Nginx | Fichiers uploadés |
| `/statics/` | Nginx | Assets Django |

## 🔐 Sécurité

✅ Backend non exposé publiquement (via Nginx uniquement)
✅ HTTPS avec Let's Encrypt
✅ Variables d'environnement isolées
✅ CORS configuré strictement
✅ Mots de passe Redis/DB générés aléatoirement

---

**EuropGreen-Solar** - Solution complète de gestion de projets solaires
Logiciel de gestion des projets d'installation solaire visant à optimiser et à centraliser la gestion des différentes étapes d'un projet d'installation solaire, depuis la visite technique initiale jusqu'à la mise en service, en passant par les démarches administratives et le suivi client
