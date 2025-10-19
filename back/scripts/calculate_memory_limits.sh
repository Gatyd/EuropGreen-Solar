#!/bin/bash

# Script d'aide au dimensionnement des ressources Docker
# Usage: ./calculate_memory_limits.sh

set -e

echo "================================================"
echo "🧮 Calculateur de limites mémoire Docker"
echo "================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher en couleur
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Détecter la RAM totale du système
if command -v free &> /dev/null; then
    TOTAL_RAM_KB=$(free | grep Mem | awk '{print $2}')
    TOTAL_RAM_MB=$((TOTAL_RAM_KB / 1024))
    TOTAL_RAM_GB=$((TOTAL_RAM_MB / 1024))
    AVAILABLE_RAM_KB=$(free | grep Mem | awk '{print $7}')
    AVAILABLE_RAM_MB=$((AVAILABLE_RAM_KB / 1024))
elif command -v vm_stat &> /dev/null; then
    # macOS
    TOTAL_RAM_BYTES=$(sysctl -n hw.memsize)
    TOTAL_RAM_MB=$((TOTAL_RAM_BYTES / 1024 / 1024))
    TOTAL_RAM_GB=$((TOTAL_RAM_MB / 1024))
    AVAILABLE_RAM_MB=$((TOTAL_RAM_MB * 70 / 100))  # Estimation 70%
else
    error "Impossible de détecter la RAM du système"
    echo "Entrez manuellement la RAM totale en GB:"
    read -r TOTAL_RAM_GB
    TOTAL_RAM_MB=$((TOTAL_RAM_GB * 1024))
    AVAILABLE_RAM_MB=$((TOTAL_RAM_MB * 70 / 100))
fi

echo "================================================"
echo "📊 Ressources système détectées"
echo "================================================"
info "RAM totale: ${TOTAL_RAM_GB} GB (${TOTAL_RAM_MB} MB)"
info "RAM disponible: ~${AVAILABLE_RAM_MB} MB"
echo ""

# Calculer la RAM à allouer à Docker
# Règle: Laisser au moins 512MB pour l'OS + 1GB pour PostgreSQL
OS_RESERVED=512
POSTGRES_RESERVED=1024
DOCKER_AVAILABLE=$((AVAILABLE_RAM_MB - OS_RESERVED - POSTGRES_RESERVED))

if [ $DOCKER_AVAILABLE -lt 0 ]; then
    DOCKER_AVAILABLE=$((TOTAL_RAM_MB * 60 / 100))  # 60% si calcul négatif
fi

info "Mémoire recommandée pour Docker: ~${DOCKER_AVAILABLE} MB"
info "  (après réservation: OS=${OS_RESERVED}MB, PostgreSQL=${POSTGRES_RESERVED}MB)"
echo ""

# Fonction de calcul des limites
calculate_limits() {
    local docker_ram=$1
    local profile=$2
    
    # Répartition proportionnelle
    # Web: 40%, Celery Worker: 30%, Redis: 20%, Celery Beat: 10%
    WEB=$((docker_ram * 40 / 100))
    CELERY_WORKER=$((docker_ram * 30 / 100))
    REDIS_CONTAINER=$((docker_ram * 20 / 100))
    CELERY_BEAT=$((docker_ram * 10 / 100))
    
    # Redis maxmemory = 50% du conteneur
    REDIS_MAX=$((REDIS_CONTAINER * 50 / 100))
    
    # Celery concurrency basé sur la RAM
    if [ $CELERY_WORKER -lt 300 ]; then
        CONCURRENCY=2
    elif [ $CELERY_WORKER -lt 600 ]; then
        CONCURRENCY=4
    elif [ $CELERY_WORKER -lt 1200 ]; then
        CONCURRENCY=6
    else
        CONCURRENCY=8
    fi
    
    echo "================================================"
    echo "📋 Configuration $profile"
    echo "================================================"
    echo "# Copiez ces valeurs dans votre fichier .env"
    echo ""
    echo "# Django/Gunicorn"
    echo "WEB_MEM_LIMIT=${WEB}m"
    echo ""
    echo "# Celery Worker"
    echo "CELERY_WORKER_MEM_LIMIT=${CELERY_WORKER}m"
    echo "CELERY_CONCURRENCY=$CONCURRENCY"
    echo ""
    echo "# Redis"
    echo "REDIS_CONTAINER_MEM_LIMIT=${REDIS_CONTAINER}m"
    echo "REDIS_MAXMEMORY=${REDIS_MAX}mb"
    echo ""
    echo "# Celery Beat"
    echo "CELERY_BEAT_MEM_LIMIT=${CELERY_BEAT}m"
    echo ""
    echo "📊 Total alloué: ~$((WEB + CELERY_WORKER + REDIS_CONTAINER + CELERY_BEAT)) MB"
    echo ""
}

# Proposer des profils selon la RAM disponible
echo "================================================"
echo "🎯 Profils recommandés"
echo "================================================"
echo ""

if [ $TOTAL_RAM_GB -ge 8 ]; then
    success "Serveur avec ressources élevées détecté (${TOTAL_RAM_GB} GB)"
    echo ""
    calculate_limits 4800 "OPTIMAL (Recommandé)"
    
    echo ""
    warning "Alternative ÉCONOMIQUE (utilise moins de RAM):"
    calculate_limits 2500 "ÉCONOMIQUE"
    
elif [ $TOTAL_RAM_GB -ge 4 ]; then
    success "Serveur avec ressources moyennes détecté (${TOTAL_RAM_GB} GB)"
    echo ""
    calculate_limits 2500 "RECOMMANDÉ"
    
    echo ""
    warning "Alternative MINIMAL (si d'autres services utilisent la RAM):"
    calculate_limits 1300 "MINIMAL"
    
elif [ $TOTAL_RAM_GB -ge 2 ]; then
    warning "Serveur avec ressources limitées détecté (${TOTAL_RAM_GB} GB)"
    echo ""
    calculate_limits 1300 "MINIMAL (Recommandé)"
    
    echo ""
    error "⚠️  Attention: 2 GB RAM est le strict minimum"
    info "Considérez une mise à niveau du serveur pour de meilleures performances"
    
else
    error "RAM insuffisante détectée (${TOTAL_RAM_GB} GB)"
    echo ""
    error "⚠️  Minimum absolu requis: 2 GB RAM"
    error "Votre serveur n'a pas assez de ressources pour ce projet"
    echo ""
    info "Options:"
    info "  1. Mettre à niveau le serveur (recommandé)"
    info "  2. Ne pas utiliser Celery (désactiver les tâches asynchrones)"
    info "  3. Utiliser un service Redis externe (Redis Cloud, AWS ElastiCache)"
    exit 1
fi

echo ""
echo "================================================"
echo "📝 Instructions d'application"
echo "================================================"
echo ""
info "1. Choisissez un profil ci-dessus"
info "2. Copiez les valeurs dans votre fichier .env"
echo ""
echo "   Exemple:"
echo "   ${BLUE}nano .env${NC}"
echo "   # Ajoutez les lignes WEB_MEM_LIMIT=..., CELERY_WORKER_MEM_LIMIT=..., etc."
echo ""
info "3. Redémarrez les services Docker:"
echo "   ${BLUE}docker-compose down && docker-compose up -d${NC}"
echo ""
info "4. Surveillez l'utilisation mémoire:"
echo "   ${BLUE}docker stats${NC}"
echo ""
echo "================================================"
echo "⚠️  Notes importantes"
echo "================================================"
echo ""
warning "- Ces calculs sont des ESTIMATIONS basées sur un usage typique"
warning "- Surveillez docker stats après le déploiement"
warning "- Ajustez si vous voyez des OOMKilled ou des performances dégradées"
warning "- Pour une haute disponibilité, utilisez un profil ÉCONOMIQUE"
echo ""
info "💡 Pour désactiver toutes les limites (déconseillé):"
echo "   Commentez toutes les variables *_MEM_LIMIT dans .env"
echo ""
info "📚 Documentation complète: DEPLOY_SECURITY_FIX.md"
echo ""

# Vérifier si .env existe et demander si on applique automatiquement
if [ -f ".env" ]; then
    echo "================================================"
    echo "🔧 Application automatique"
    echo "================================================"
    echo ""
    warning "Fichier .env détecté"
    echo "Voulez-vous appliquer automatiquement un profil? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo "Choisissez un profil:"
        
        if [ $TOTAL_RAM_GB -ge 8 ]; then
            echo "  1) OPTIMAL (4.8 GB)"
            echo "  2) ÉCONOMIQUE (2.5 GB)"
            echo "  3) Annuler"
            read -r choice
            case $choice in
                1) TARGET_RAM=4800; PROFILE="OPTIMAL" ;;
                2) TARGET_RAM=2500; PROFILE="ÉCONOMIQUE" ;;
                *) echo "Annulé"; exit 0 ;;
            esac
        elif [ $TOTAL_RAM_GB -ge 4 ]; then
            echo "  1) RECOMMANDÉ (2.5 GB)"
            echo "  2) MINIMAL (1.3 GB)"
            echo "  3) Annuler"
            read -r choice
            case $choice in
                1) TARGET_RAM=2500; PROFILE="RECOMMANDÉ" ;;
                2) TARGET_RAM=1300; PROFILE="MINIMAL" ;;
                *) echo "Annulé"; exit 0 ;;
            esac
        else
            echo "  1) MINIMAL (1.3 GB)"
            echo "  2) Annuler"
            read -r choice
            case $choice in
                1) TARGET_RAM=1300; PROFILE="MINIMAL" ;;
                *) echo "Annulé"; exit 0 ;;
            esac
        fi
        
        # Calculer les valeurs
        WEB=$((TARGET_RAM * 40 / 100))
        CELERY_WORKER=$((TARGET_RAM * 30 / 100))
        REDIS_CONTAINER=$((TARGET_RAM * 20 / 100))
        CELERY_BEAT=$((TARGET_RAM * 10 / 100))
        REDIS_MAX=$((REDIS_CONTAINER * 50 / 100))
        
        if [ $CELERY_WORKER -lt 300 ]; then
            CONCURRENCY=2
        elif [ $CELERY_WORKER -lt 600 ]; then
            CONCURRENCY=4
        elif [ $CELERY_WORKER -lt 1200 ]; then
            CONCURRENCY=6
        else
            CONCURRENCY=8
        fi
        
        # Backup .env
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        info "Backup créé: .env.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Supprimer les anciennes valeurs
        sed -i.tmp '/^WEB_MEM_LIMIT=/d' .env
        sed -i.tmp '/^CELERY_WORKER_MEM_LIMIT=/d' .env
        sed -i.tmp '/^CELERY_CONCURRENCY=/d' .env
        sed -i.tmp '/^REDIS_CONTAINER_MEM_LIMIT=/d' .env
        sed -i.tmp '/^REDIS_MAXMEMORY=/d' .env
        sed -i.tmp '/^CELERY_BEAT_MEM_LIMIT=/d' .env
        rm -f .env.tmp
        
        # Ajouter les nouvelles valeurs
        cat >> .env << EOF

# Configuration mémoire Docker - Profil: $PROFILE
# Généré le: $(date)
WEB_MEM_LIMIT=${WEB}m
CELERY_WORKER_MEM_LIMIT=${CELERY_WORKER}m
CELERY_CONCURRENCY=$CONCURRENCY
REDIS_CONTAINER_MEM_LIMIT=${REDIS_CONTAINER}m
REDIS_MAXMEMORY=${REDIS_MAX}mb
CELERY_BEAT_MEM_LIMIT=${CELERY_BEAT}m
EOF
        
        success "Configuration appliquée au fichier .env"
        echo ""
        info "Redémarrez maintenant les services:"
        echo "   ${BLUE}docker-compose down && docker-compose up -d${NC}"
    fi
fi

echo ""
success "Script terminé"
echo ""
