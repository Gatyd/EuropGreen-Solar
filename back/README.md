## Installation

### Développement local (sans Docker)

1. Ouvrir le dossier dans un terminal

2. Aller dans le dossier du backend:
```bash
cd back
```

3. Créer un environnement virtuel nommé venv:
```bash
python -m venv venv
``` 

4. Activer l'environnement virtuel
```bash
venv\Scripts\activate
```

5. Installer Django et les dépendances du projet:
```bash
pip install -r requirements.txt
```

6. Demarrer le serveur d'application django:
```bash
python manage.py runserver
```

### Production (avec Docker) - **RECOMMANDÉ**

```bash
# Voir le guide complet : DEPLOYMENT_GUIDE.md
docker-compose up -d
```

## 📚 Documentation

**📘 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guide complet (déploiement, configuration, sécurité, dépannage)

**Quick Start Docker :**
```bash
cp .env.example .env
nano .env  # Configurer REDIS_PASSWORD, DB_*, etc.
docker-compose up -d
```
