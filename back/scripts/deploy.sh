#!/bin/bash

echo "🚀 Mise à jour du code..."
git pull origin main

echo "🔧 Reconstruction du conteneur..."
docker-compose down
docker-compose build
docker-compose up -d

echo "🧩 Migrations..."
docker-compose exec web python manage.py migrate

echo "📦 Collecte des fichiers statiques..."
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ Déploiement terminé !"
