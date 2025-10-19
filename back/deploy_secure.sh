#!/bin/bash

# Script de déploiement sécurisé avec corrections Redis
# Usage: ./deploy_secure.sh

set -e  # Arrêt en cas d'erreur

echo "================================================"
echo "🔒 Déploiement sécurisé - EuropGreen-Solar"
echo "================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si on est dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erreur: docker-compose.yml non trouvé${NC}"
    echo "Exécutez ce script depuis le répertoire back/"
    exit 1
fi

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    echo "Création depuis .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

# Vérifier si REDIS_PASSWORD est défini
REDIS_PASS=$(grep "^REDIS_PASSWORD=" .env | cut -d '=' -f2 || echo "")

if [ -z "$REDIS_PASS" ] || [ "$REDIS_PASS" == "changeme_redis_password_MUST_BE_CHANGED" ]; then
    echo ""
    echo -e "${RED}❌ REDIS_PASSWORD non défini ou utilise la valeur par défaut${NC}"
    echo ""
    echo "Pour sécuriser Redis, générez un mot de passe fort:"
    echo ""
    echo -e "${GREEN}# Générer un mot de passe (Linux/Mac)${NC}"
    echo "openssl rand -base64 32"
    echo ""
    echo -e "${GREEN}# Ou utilisez cette commande complète:${NC}"
    echo "echo \"REDIS_PASSWORD=\$(openssl rand -base64 32)\" >> .env"
    echo ""
    echo -e "${YELLOW}Voulez-vous générer un mot de passe automatiquement? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        NEW_PASS=$(openssl rand -base64 32)
        
        # Retirer l'ancienne ligne si elle existe
        sed -i.bak '/^REDIS_PASSWORD=/d' .env
        
        # Ajouter la nouvelle
        echo "REDIS_PASSWORD=$NEW_PASS" >> .env
        
        echo -e "${GREEN}✅ REDIS_PASSWORD généré et ajouté au fichier .env${NC}"
    else
        echo -e "${RED}Déploiement annulé. Veuillez configurer REDIS_PASSWORD manuellement.${NC}"
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "📋 Étape 1/5 : Arrêt des services"
echo "================================================"
docker-compose down
echo -e "${GREEN}✅ Services arrêtés${NC}"

echo ""
echo "================================================"
echo "📋 Étape 2/5 : Nettoyage des données Redis"
echo "================================================"
echo -e "${YELLOW}⚠️  Les données Redis seront supprimées pour appliquer la nouvelle config${NC}"
echo "Continuer? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker volume rm back_redis_data 2>/dev/null || echo "Volume redis_data déjà supprimé"
    echo -e "${GREEN}✅ Données Redis nettoyées${NC}"
else
    echo -e "${YELLOW}Conservation des données Redis (peut causer des problèmes)${NC}"
fi

echo ""
echo "================================================"
echo "📋 Étape 3/5 : Rebuild des images Docker"
echo "================================================"
docker-compose build --no-cache
echo -e "${GREEN}✅ Images reconstruites${NC}"

echo ""
echo "================================================"
echo "📋 Étape 4/5 : Démarrage des services"
echo "================================================"
docker-compose up -d
echo -e "${GREEN}✅ Services démarrés${NC}"

# Attendre que Redis soit prêt
echo ""
echo "Attente du démarrage de Redis (10 secondes)..."
sleep 10

echo ""
echo "================================================"
echo "📋 Étape 5/5 : Vérifications de sécurité"
echo "================================================"

# Vérifier que Redis n'est pas exposé
echo ""
echo "🔍 Vérification 1: Redis ne doit PAS être exposé sur le port 6379"
REDIS_EXPOSED=$(docker-compose port redis 6379 2>/dev/null || echo "")

if [ -z "$REDIS_EXPOSED" ]; then
    echo -e "${GREEN}✅ Redis n'est PAS exposé publiquement (CORRECT)${NC}"
else
    echo -e "${RED}❌ ERREUR: Redis est exposé sur $REDIS_EXPOSED${NC}"
    echo "   Vérifiez docker-compose.yml (section 'ports' doit être commentée)"
fi

# Test connexion Redis avec mot de passe
echo ""
echo "🔍 Vérification 2: Authentification Redis"
REDIS_AUTH=$(docker-compose exec -T redis redis-cli -a "$REDIS_PASS" PING 2>/dev/null || echo "FAILED")

if [ "$REDIS_AUTH" == "PONG" ]; then
    echo -e "${GREEN}✅ Redis répond correctement avec authentification${NC}"
else
    echo -e "${RED}❌ ERREUR: Redis ne répond pas correctement${NC}"
    echo "   Vérifiez les logs: docker-compose logs redis"
fi

# Test connexion Celery
echo ""
echo "🔍 Vérification 3: Celery worker"
sleep 5  # Attendre que Celery démarre
CELERY_STATUS=$(docker-compose logs celery-worker 2>&1 | grep -i "ready\|connected" | tail -1 || echo "")

if [ ! -z "$CELERY_STATUS" ]; then
    echo -e "${GREEN}✅ Celery worker semble fonctionner${NC}"
    echo "   $CELERY_STATUS"
else
    echo -e "${YELLOW}⚠️  Statut Celery incertain, vérifiez les logs${NC}"
fi

echo ""
echo "================================================"
echo "📊 Statut des conteneurs"
echo "================================================"
docker-compose ps

echo ""
echo "================================================"
echo "🎉 Déploiement terminé!"
echo "================================================"
echo ""
echo "📝 Commandes utiles:"
echo ""
echo "  # Voir les logs en temps réel"
echo "  docker-compose logs -f"
echo ""
echo "  # Logs d'un service spécifique"
echo "  docker-compose logs -f celery-worker"
echo "  docker-compose logs -f redis"
echo ""
echo "  # Statistiques ressources"
echo "  docker stats"
echo ""
echo "  # Test Redis manuel"
echo "  docker-compose exec redis redis-cli -a \"\$REDIS_PASSWORD\" PING"
echo ""
echo "  # Restart d'un service"
echo "  docker-compose restart celery-worker"
echo ""

# Afficher les dernières lignes des logs Redis pour détecter les attaques
echo "================================================"
echo "🔍 Derniers logs Redis (attaques détectées?)"
echo "================================================"
docker-compose logs redis | grep -i "security\|attack" | tail -5 || echo "Aucune attaque détectée récemment"

echo ""
echo -e "${GREEN}✅ Déploiement sécurisé terminé avec succès!${NC}"
echo ""
