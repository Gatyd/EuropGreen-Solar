#!/bin/bash
# Script de déploiement automatique

set -e

echo "🚀 Déploiement EuropGreen Solar"

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant"
    echo "Copiez .env.example vers .env et configurez-le"
    exit 1
fi

# Pull du code
echo "📥 Mise à jour du code..."
git pull origin main

# Build des images
echo "🔨 Build des images Docker..."
docker compose build

# Arrêt des anciens conteneurs
echo "⏹️  Arrêt des anciens conteneurs..."
docker compose down

# Démarrage
echo "▶️  Démarrage des services..."
docker compose up -d

# Attente
echo "⏳ Attente du démarrage..."
sleep 10

# Migrations
echo "🗃️  Application des migrations..."
docker compose exec backend python manage.py migrate --noinput

# Collecte statiques
echo "📄 Collecte des fichiers statiques..."
docker compose exec backend python manage.py collectstatic --noinput

# Vérification
echo "🏥 Vérification des services..."
docker compose ps

echo "✅ Déploiement terminé !"
echo ""
echo "🌐 Accès:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}')"
echo "  Admin:    http://$(hostname -I | awk '{print $1}')/admin/"
