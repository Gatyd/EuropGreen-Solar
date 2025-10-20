# 🚀 Guide de Déploiement Complet - EuropGreen Solar

## 📋 Vue d'ensemble

**Architecture :** Frontend (Nuxt 3) + Backend (Django) + Nginx reverse proxy
**Accès :** 
- Frontend : `https://votre-domaine.com`
- API Backend : `https://votre-domaine.com/api/`
- Admin Django : `https://votre-domaine.com/admin/`

---

## ⚡ Déploiement Rapide (5 minutes)

### 1. **Sur votre serveur**

```bash
# Cloner le projet
git clone https://github.com/Gatyd/EuropGreen-Solar.git
cd EuropGreen-Solar

# Copier et configurer l'environnement
cp .env.example .env
nano .env  # Modifier les valeurs (voir section Configuration)

# Lancer tout
docker compose up -d

# Appliquer les migrations
docker compose exec backend python manage.py migrate

# Collecter les fichiers statiques
docker compose exec backend python manage.py collectstatic --noinput

# Créer un superuser
docker compose exec backend python manage.py createsuperuser
```

✅ **C'est tout !** Votre application tourne sur `http://votre-ip`

---

## 🔧 Configuration du .env

**Valeurs à OBLIGATOIREMENT changer :**

```bash
# 1. Domaine
ALLOWED_HOSTS=mon-domaine.com,www.mon-domaine.com
FRONTEND_URL=https://mon-domaine.com

# 2. Base de données (générer mots de passe forts)
DB_PASSWORD=$(openssl rand -base64 32)

# 3. Redis (générer mot de passe fort)
REDIS_PASSWORD=$(openssl rand -base64 32)

# 4. Email
EMAIL_HOST_USER=mon-email@gmail.com
EMAIL_HOST_PASSWORD=mon-app-password
SAV_EMAIL=sav@mon-domaine.com
```

---

## 🔒 Activer HTTPS (Let's Encrypt)

### Option A : Certbot automatique (recommandé)

```bash
# 1. Installer Certbot
sudo apt update
sudo apt install certbot

# 2. Arrêter temporairement Nginx
docker compose stop nginx

# 3. Obtenir le certificat
sudo certbot certonly --standalone -d mon-domaine.com -d www.mon-domaine.com

# 4. Copier les certificats dans le projet
sudo cp /etc/letsencrypt/live/mon-domaine.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/mon-domaine.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*.pem

# 5. Activer HTTPS dans nginx.conf
nano nginx/nginx.conf
# Décommenter le bloc "server { listen 443 ssl... }"
# Commenter ou supprimer "return 301" dans le bloc HTTP

# 6. Redémarrer
docker compose up -d
```

### Option B : Renouvellement automatique

```bash
# Créer un script de renouvellement
sudo crontab -e

# Ajouter cette ligne (renouvellement tous les lundis à 3h)
0 3 * * 1 certbot renew --quiet && cp /etc/letsencrypt/live/mon-domaine.com/*.pem /root/EuropGreen-Solar/nginx/ssl/ && docker compose -f /root/EuropGreen-Solar/docker-compose.yml restart nginx
```

---

## 📁 Gestion des Fichiers Media & Static

### Fichiers statiques (CSS, JS, images du code)

**Automatique** : Collectés dans le volume `static_data` et servis par Nginx

```bash
# Recollecte si vous ajoutez des fichiers statiques
docker compose exec backend python manage.py collectstatic --noinput
```

### Fichiers media (uploads utilisateurs)

**Persistance** : Stockés dans le volume Docker `media_data`

**Backup** :
```bash
# Sauvegarder les media
docker run --rm -v europgreen-solar_media_data:/data -v $(pwd):/backup alpine tar czf /backup/media-backup-$(date +%Y%m%d).tar.gz /data

# Restaurer
docker run --rm -v europgreen-solar_media_data:/data -v $(pwd):/backup alpine tar xzf /backup/media-backup-YYYYMMDD.tar.gz -C /
```

---

## 🌐 URLs et Séparation des Services

**Avec Nginx, tout passe par le même domaine mais est routé intelligemment :**

| URL | Service | Utilisation |
|-----|---------|-------------|
| `https://mon-domaine.com/` | Frontend (Nuxt) | Interface utilisateur |
| `https://mon-domaine.com/api/*` | Backend (Django) | API REST |
| `https://mon-domaine.com/admin/` | Backend (Django) | Interface admin |
| `https://mon-domaine.com/media/*` | Nginx | Fichiers uploadés |
| `https://mon-domaine.com/statics/*` | Nginx | CSS/JS Django |

**Le backend n'est PAS exposé directement** → Sécurité renforcée ✅

---

## 🔄 Mise à Jour du Code

```bash
cd ~/EuropGreen-Solar

# 1. Pull les changements
git pull origin main

# 2. Rebuild et redémarrage
docker compose build
docker compose up -d

# 3. Migrations si nécessaire
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

---

## 📊 Commandes Utiles

```bash
# Voir les logs
docker compose logs -f                    # Tous les services
docker compose logs -f frontend           # Frontend seulement
docker compose logs -f backend            # Backend seulement

# Redémarrer un service
docker compose restart nginx

# Accéder au shell Django
docker compose exec backend python manage.py shell

# Voir l'état des services
docker compose ps

# Arrêter tout
docker compose down

# Nettoyer (ATTENTION: supprime les volumes)
docker compose down -v
```

---

## 🆘 Dépannage

### Frontend ne charge pas
```bash
docker compose logs frontend
# Vérifier que PROXY_URL=http://backend:8000 dans .env
```

### Erreur 502 Bad Gateway
```bash
docker compose ps  # Vérifier que backend est "Up"
docker compose restart backend nginx
```

### Erreur CORS
```bash
# Vérifier que FRONTEND_URL dans .env correspond au domaine public
nano .env
docker compose restart backend
```

### Base de données vide après redémarrage
```bash
# Les volumes sont persistants, sauf si vous faites "down -v"
# Restaurer un backup si nécessaire
```

---

## 🔐 Checklist Sécurité

- [ ] `.env` n'est PAS commité (dans `.gitignore`)
- [ ] Mots de passe forts générés (DB, Redis)
- [ ] HTTPS activé avec Let's Encrypt
- [ ] `DEBUG=False` en production
- [ ] Firewall configuré (ports 80, 443 uniquement)
- [ ] Backend non exposé directement (Nginx uniquement)
- [ ] Backups réguliers des volumes

---

## 📈 Monitoring (Optionnel)

```bash
# Voir l'utilisation des ressources
docker stats

# Espace disque
df -h
docker system df
```

---

**🎯 Support :** En cas de problème, consultez les logs avec `docker compose logs`
