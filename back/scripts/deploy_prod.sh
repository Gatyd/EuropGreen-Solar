#!/bin/bash
# Script de déploiement pour serveur Linux de production

set -e  # Arrêt si erreur

echo "🚀 Déploiement EuropGreen-Solar - Production"

# 1. Créer les dossiers si nécessaire
echo "📁 Création des dossiers de données..."
sudo mkdir -p /var/www/mon_projet/media
sudo mkdir -p /var/www/mon_projet/pgdata

# 2. Définir les permissions
echo "🔒 Configuration des permissions..."
sudo chown -R $USER:$USER /var/www/mon_projet/media
sudo chmod -R 755 /var/www/mon_projet/media

# 3. Vérifier le fichier .env
if [ ! -f .env ]; then
    echo "❌ Erreur: Fichier .env manquant"
    echo "Copiez .env.example vers .env et configurez-le"
    exit 1
fi

# 4. Vérifier que DEBUG=False
if grep -q "^DEBUG=True" .env; then
    echo "⚠️  ATTENTION: DEBUG=True détecté dans .env"
    echo "En production, assurez-vous que DEBUG=False"
    read -p "Continuer quand même ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 5. Pull des dernières images
echo "📦 Récupération des images Docker..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# 6. Build des images
echo "🔨 Build des images Docker..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 7. Arrêt des anciens conteneurs
echo "⏹️  Arrêt des anciens conteneurs..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# 8. Démarrage des nouveaux conteneurs
echo "▶️  Démarrage des nouveaux conteneurs..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 9. Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# 10. Migrations de base de données
echo "🗃️  Application des migrations..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# 11. Collecte des fichiers statiques
echo "📄 Collecte des fichiers statiques..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# 12. Vérification de la santé des services
echo "🏥 Vérification de la santé des services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo "✅ Déploiement terminé !"
echo ""
echo "📋 Commandes utiles:"
echo "  Logs web:        docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f web"
echo "  Logs celery:     docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f celery-worker"
echo "  Statut:          docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps"
echo "  Arrêt:           docker-compose -f docker-compose.yml -f docker-compose.prod.yml down"
