# 📘 Guide de déploiement et maintenance - EuropGreen-Solar

> **Documentation unique** - Tout ce qu'il faut savoir pour déployer et maintenir le backend

## 📚 Table des matières

1. [Déploiement rapide](#-déploiement-rapide)
2. [Configuration Redis & Celery](#-configuration-redis--celery)
3. [Dimensionnement mémoire](#-dimensionnement-mémoire)
4. [Sécurité](#-sécurité)
5. [Dépannage](#-dépannage)
6. [Monitoring](#-monitoring)

---

## 🚀 Déploiement rapide

### Prérequis
- Docker & Docker Compose installés
- Git
- Serveur avec minimum 2 GB RAM (4 GB recommandé)

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/Gatyd/EuropGreen-Solar.git
cd EuropGreen-Solar/back

# 2. Créer le fichier .env
cp .env.example .env
nano .env

# 3. Configuration minimale requise dans .env
REDIS_PASSWORD=VotreMotDePasseFort123!  # CHANGEZ CECI
REDIS_HOST=redis                         # Pour Docker
DB_NAME=votre_db
DB_USER=votre_user
DB_PASSWORD=votre_password

# 4. Démarrer les services
docker-compose up -d

# 5. Migrations base de données
docker-compose exec web python manage.py migrate

# 6. Créer un superuser
docker-compose exec web python manage.py createsuperuser

# 7. Vérifier que tout fonctionne
docker-compose ps    # Tous les services doivent être "Up"
docker-compose logs -f  # Surveiller les logs
```

### Services démarrés

| Service | Port | Description |
|---------|------|-------------|
| **web** | 8000 | Django + Gunicorn (API backend) |
| **db** | 5432 | PostgreSQL (non exposé) |
| **redis** | - | Redis (non exposé, sécurisé) |
| **celery-worker** | - | Workers pour tâches asynchrones |
| **celery-beat** | - | Planificateur de tâches périodiques |

---

## 🔧 Configuration Redis & Celery

### Variables d'environnement (.env)

```bash
# Redis - OBLIGATOIRE pour Docker
REDIS_PASSWORD=VotreMotDePasseFort  # Min 12 caractères
REDIS_HOST=redis                     # "redis" pour Docker, "localhost" pour dev local
REDIS_PORT=6379
REDIS_DB=0

# ⚠️ NE PAS définir CELERY_BROKER_URL manuellement
# C'est généré automatiquement dans settings.py avec le mot de passe

# Système de rappels (optionnel)
REMINDER_DAYS_BEFORE=3    # Rappel X jours avant échéance
REMINDER_HOURS_BEFORE=3   # Rappel X heures avant échéance
REMINDER_TIME_HOUR=8      # Heure des rappels quotidiens (0-23)
```

### Erreurs courantes

**❌ `Connection refused` sur Redis**
```bash
# Cause : REDIS_HOST=localhost dans .env alors que vous utilisez Docker
# Solution : Changez en REDIS_HOST=redis
nano .env  # Modifier REDIS_HOST=redis
docker-compose restart celery-worker celery-beat
```

**❌ `NOAUTH Authentication required`**
```bash
# Cause : REDIS_PASSWORD pas défini ou incorrect
# Solution : Vérifier .env et redémarrer
docker-compose restart
```

---

## 💾 Dimensionnement mémoire

### Configuration automatique (Recommandé)

```bash
# Script Python qui détecte votre RAM et propose des profils
python calculate_memory_limits.py

# Suit les instructions et applique au .env
```

### Configuration manuelle selon votre serveur

**Serveur 2 GB RAM (Minimal)**
```bash
# Dans .env
WEB_MEM_LIMIT=520m
CELERY_WORKER_MEM_LIMIT=390m
CELERY_CONCURRENCY=2
REDIS_CONTAINER_MEM_LIMIT=260m
REDIS_MAXMEMORY=130mb
CELERY_BEAT_MEM_LIMIT=130m
```

**Serveur 4 GB RAM (Recommandé)**
```bash
# Dans .env
WEB_MEM_LIMIT=1000m
CELERY_WORKER_MEM_LIMIT=750m
CELERY_CONCURRENCY=4
REDIS_CONTAINER_MEM_LIMIT=500m
REDIS_MAXMEMORY=250mb
CELERY_BEAT_MEM_LIMIT=250m
```

**Serveur 8+ GB RAM (Optimal)**
```bash
# Dans .env
WEB_MEM_LIMIT=1920m
CELERY_WORKER_MEM_LIMIT=1440m
CELERY_CONCURRENCY=8
REDIS_CONTAINER_MEM_LIMIT=960m
REDIS_MAXMEMORY=480mb
CELERY_BEAT_MEM_LIMIT=480m
```

### Pas de limites (Développement local)

```bash
# Option 1 : Ne rien mettre dans .env
# Les valeurs par défaut seront utilisées

# Option 2 : Commenter les mem_limit dans docker-compose.yml
```

---

## 🔒 Sécurité

### Checklist sécurité

- ✅ **Redis avec mot de passe** : `REDIS_PASSWORD` défini (32+ caractères)
- ✅ **Redis non exposé** : Port 6379 NOT dans `ports:` du docker-compose.yml
- ✅ **Commandes Redis désactivées** : CONFIG, FLUSHDB, FLUSHALL renommées
- ✅ **Firewall** : Port 6379 bloqué, seul 8000 ouvert
- ✅ **HTTPS en production** : Reverse proxy (Nginx/Caddy) devant Django

### Activer le firewall (Production Linux)

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 8000/tcp    # Django
sudo ufw allow 22/tcp      # SSH
sudo ufw deny 6379/tcp     # Bloquer Redis
sudo ufw enable
sudo ufw status
```

### Tester la sécurité

```bash
# Depuis un autre serveur, tester si Redis est exposé
redis-cli -h VOTRE_IP_SERVEUR ping
# Doit retourner : "Connection refused" ou "timeout" (BIEN)
# NE DOIT PAS retourner : "PONG" ou "NOAUTH" (MAUVAIS)

# Script de test automatisé
cd back
python test_redis_security.py
```

---

## 🔍 Dépannage

### Problème : Services ne démarrent pas

```bash
# Voir les logs
docker-compose logs

# Logs d'un service spécifique
docker-compose logs celery-worker
docker-compose logs web

# Redémarrer un service
docker-compose restart celery-worker
```

### Problème : Celery ne se connecte pas à Redis

**Symptôme** : `Connection refused localhost:6379`

**Solutions** :
```bash
# 1. Vérifier .env
cat .env | grep REDIS_HOST
# Doit afficher : REDIS_HOST=redis (pas localhost)

# 2. Si localhost, corriger
nano .env
# Changer en : REDIS_HOST=redis

# 3. Redémarrer
docker-compose restart celery-worker celery-beat

# 4. Vérifier les logs
docker-compose logs -f celery-worker
# Doit afficher : "celery@hostname ready"
```

### Problème : OOMKilled (Mémoire insuffisante)

```bash
# Vérifier les logs
docker-compose logs | grep -i oom

# Solution 1 : Augmenter les limites dans .env
WEB_MEM_LIMIT=1500m  # +50%

# Solution 2 : Réduire la concurrence
CELERY_CONCURRENCY=2  # Au lieu de 4

# Solution 3 : Upgrade du serveur
# Passer de 2 GB à 4 GB RAM
```

### Problème : Build Docker trop long

**Cause** : Playwright s'installe 3 fois (web, celery-worker, celery-beat)

**Solution** : ✅ Déjà corrigé - Utilise des Dockerfiles séparés
- `Dockerfile` → Web (avec Playwright)
- `Dockerfile.celery` → Celery (sans Playwright, léger)

### Problème : Emails asynchrones ne partent pas

```bash
# Vérifier Celery worker
docker-compose logs celery-worker

# Tester manuellement
docker-compose exec web python manage.py shell
>>> from EuropGreenSolar.email_utils import send_mail
>>> send_mail("Test", "Message", ["test@example.com"], async_send=True)
# Vérifier les logs Celery pour voir la tâche

# Si erreur de sérialisation
# Vérifier que le contexte ne contient pas d'objets Django non sérialisables
```

---

## 📊 Monitoring

### Commandes essentielles

```bash
# Utilisation mémoire/CPU en temps réel
docker stats

# État des services
docker-compose ps

# Logs en continu
docker-compose logs -f

# Logs des 100 dernières lignes d'un service
docker-compose logs --tail=100 celery-worker

# Vérifier la santé de Celery
docker-compose exec celery-worker celery -A EuropGreenSolar inspect ping

# Statistiques Redis
docker-compose exec redis redis-cli -a "$REDIS_PASSWORD" INFO memory
```

### Indicateurs à surveiller

| Indicateur | Valeur normale | Action si anormal |
|------------|----------------|-------------------|
| Mémoire utilisée | 60-80% limite | <50%: réduire limite<br>>90%: augmenter |
| CPU | <70% | >80%: optimiser code ou upgrade |
| Celery tasks queued | <10 | >100: augmenter workers |
| Redis memory | <80% maxmemory | >90%: augmenter maxmemory |

### Script de monitoring (optionnel)

```bash
# Créer /var/www/mon_projet/monitor.sh
#!/bin/bash
while true; do
    echo "=== $(date) ===" >> /var/log/docker_stats.log
    docker stats --no-stream >> /var/log/docker_stats.log
    sleep 300  # Toutes les 5 minutes
done

# Lancer en arrière-plan
nohup ./monitor.sh &
```

---

## 📝 Checklist déploiement production

Avant de mettre en production, vérifiez :

- [ ] `.env` créé avec valeurs de production (pas .env.example)
- [ ] `REDIS_PASSWORD` défini (32+ caractères)
- [ ] `REDIS_HOST=redis` (pas localhost)
- [ ] `DEBUG=False` dans settings.py
- [ ] Base de données PostgreSQL (pas SQLite)
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Limites mémoire définies selon RAM serveur
- [ ] Migrations appliquées (`python manage.py migrate`)
- [ ] Collectstatic exécuté (`python manage.py collectstatic`)
- [ ] Firewall activé (UFW/iptables)
- [ ] Redis NON exposé (test depuis extérieur)
- [ ] HTTPS configuré (reverse proxy)
- [ ] Backup base de données planifié
- [ ] Monitoring actif (`docker stats`)
- [ ] Logs rotatifs configurés

---

## 🆘 Support rapide

### Redémarrage complet

```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Rebuild complet (en cas de gros changements)

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Nettoyage total (ATTENTION : supprime les données)

```bash
docker-compose down -v  # -v supprime les volumes (DB, Redis)
docker-compose up -d
# Puis réappliquer les migrations et créer superuser
```

---

## 📚 Ressources

- **Script dimensionnement** : `python calculate_memory_limits.py`
- **Script tests sécurité** : `python test_redis_security.py`
- **Docker Docs** : https://docs.docker.com/compose/
- **Celery Docs** : https://docs.celeryproject.org/
- **Django Docs** : https://docs.djangoproject.com/

---

**Dernière mise à jour** : 19 octobre 2025  
**Version** : 2.0 - Documentation consolidée
