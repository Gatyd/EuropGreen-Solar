"""
Calculateur de limites mémoire Docker pour EuropGreen-Solar
Usage: python calculate_memory_limits.py
"""

import platform
import subprocess
import os
from datetime import datetime

# Couleurs pour Windows/Linux
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = ""
    class Style:
        RESET_ALL = ""

def info(text):
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def header(text):
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def get_total_ram():
    """Détecter la RAM totale du système"""
    system = platform.system()
    
    try:
        if system == "Linux":
            # Linux avec /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        ram_kb = int(line.split()[1])
                        return ram_kb // 1024  # Convert to MB
        
        elif system == "Windows":
            # Windows avec wmic
            output = subprocess.check_output(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                                           text=True)
            ram_bytes = int(output.strip().split('\n')[1])
            return ram_bytes // (1024 * 1024)  # Convert to MB
        
        elif system == "Darwin":
            # macOS
            output = subprocess.check_output(['sysctl', '-n', 'hw.memsize'], text=True)
            ram_bytes = int(output.strip())
            return ram_bytes // (1024 * 1024)  # Convert to MB
    
    except Exception as e:
        error(f"Impossible de détecter automatiquement la RAM: {e}")
        return None

def calculate_limits(docker_ram_mb, profile_name):
    """Calculer les limites mémoire pour chaque service"""
    # Répartition: Web 40%, Celery Worker 30%, Redis 20%, Celery Beat 10%
    web = int(docker_ram_mb * 0.40)
    celery_worker = int(docker_ram_mb * 0.30)
    redis_container = int(docker_ram_mb * 0.20)
    celery_beat = int(docker_ram_mb * 0.10)
    
    # Redis maxmemory = 50% du conteneur
    redis_max = int(redis_container * 0.50)
    
    # Celery concurrency selon RAM
    if celery_worker < 300:
        concurrency = 2
    elif celery_worker < 600:
        concurrency = 4
    elif celery_worker < 1200:
        concurrency = 6
    else:
        concurrency = 8
    
    total = web + celery_worker + redis_container + celery_beat
    
    return {
        'profile': profile_name,
        'web': web,
        'celery_worker': celery_worker,
        'redis_container': redis_container,
        'redis_max': redis_max,
        'celery_beat': celery_beat,
        'concurrency': concurrency,
        'total': total
    }

def display_config(config):
    """Afficher une configuration"""
    header(f"Configuration {config['profile']}")
    
    print("# Copiez ces valeurs dans votre fichier .env\n")
    print("# Django/Gunicorn")
    print(f"WEB_MEM_LIMIT={config['web']}m\n")
    print("# Celery Worker")
    print(f"CELERY_WORKER_MEM_LIMIT={config['celery_worker']}m")
    print(f"CELERY_CONCURRENCY={config['concurrency']}\n")
    print("# Redis")
    print(f"REDIS_CONTAINER_MEM_LIMIT={config['redis_container']}m")
    print(f"REDIS_MAXMEMORY={config['redis_max']}mb\n")
    print("# Celery Beat")
    print(f"CELERY_BEAT_MEM_LIMIT={config['celery_beat']}m\n")
    print(f"📊 Total alloué: ~{config['total']} MB\n")

def apply_to_env(config):
    """Appliquer la configuration au fichier .env"""
    if not os.path.exists('.env'):
        error("Fichier .env non trouvé")
        return False
    
    # Backup
    backup_name = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open('.env', 'r') as f:
            content = f.read()
        with open(backup_name, 'w') as f:
            f.write(content)
        info(f"Backup créé: {backup_name}")
    except Exception as e:
        error(f"Erreur lors du backup: {e}")
        return False
    
    # Lire .env et supprimer les anciennes valeurs
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Filtrer les lignes à remplacer
        new_lines = []
        for line in lines:
            if not any(line.startswith(key) for key in [
                'WEB_MEM_LIMIT=',
                'CELERY_WORKER_MEM_LIMIT=',
                'CELERY_CONCURRENCY=',
                'REDIS_CONTAINER_MEM_LIMIT=',
                'REDIS_MAXMEMORY=',
                'CELERY_BEAT_MEM_LIMIT='
            ]):
                new_lines.append(line)
        
        # Ajouter les nouvelles valeurs
        new_lines.append(f"\n# Configuration mémoire Docker - Profil: {config['profile']}\n")
        new_lines.append(f"# Généré le: {datetime.now()}\n")
        new_lines.append(f"WEB_MEM_LIMIT={config['web']}m\n")
        new_lines.append(f"CELERY_WORKER_MEM_LIMIT={config['celery_worker']}m\n")
        new_lines.append(f"CELERY_CONCURRENCY={config['concurrency']}\n")
        new_lines.append(f"REDIS_CONTAINER_MEM_LIMIT={config['redis_container']}m\n")
        new_lines.append(f"REDIS_MAXMEMORY={config['redis_max']}mb\n")
        new_lines.append(f"CELERY_BEAT_MEM_LIMIT={config['celery_beat']}m\n")
        
        # Écrire
        with open('.env', 'w') as f:
            f.writelines(new_lines)
        
        success("Configuration appliquée au fichier .env")
        return True
        
    except Exception as e:
        error(f"Erreur lors de l'écriture: {e}")
        return False

def main():
    print(f"\n{Fore.GREEN}{'*' * 60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}* Calculateur de limites mémoire Docker{Style.RESET_ALL}")
    print(f"{Fore.GREEN}* EuropGreen-Solar{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'*' * 60}{Style.RESET_ALL}")
    
    # Détecter la RAM
    header("Détection des ressources système")
    
    total_ram_mb = get_total_ram()
    
    if total_ram_mb is None:
        print("\nEntrez manuellement la RAM totale de votre serveur (en GB):")
        try:
            total_ram_gb = int(input("RAM (GB): "))
            total_ram_mb = total_ram_gb * 1024
        except ValueError:
            error("Valeur invalide")
            return
    
    total_ram_gb = total_ram_mb // 1024
    
    info(f"RAM totale: {total_ram_gb} GB ({total_ram_mb} MB)")
    
    # Calculer la RAM disponible pour Docker
    os_reserved = 512  # MB pour l'OS
    postgres_reserved = 1024  # MB pour PostgreSQL
    docker_available = int(total_ram_mb * 0.70) - os_reserved - postgres_reserved
    
    if docker_available < 0:
        docker_available = int(total_ram_mb * 0.60)
    
    info(f"Mémoire recommandée pour Docker: ~{docker_available} MB")
    info(f"  (après réservation: OS={os_reserved}MB, PostgreSQL={postgres_reserved}MB)")
    
    # Générer les profils selon la RAM
    print()
    header("Profils recommandés")
    
    profiles = []
    
    if total_ram_gb >= 8:
        success(f"Serveur avec ressources élevées détecté ({total_ram_gb} GB)")
        print()
        
        optimal = calculate_limits(4800, "OPTIMAL (Recommandé)")
        display_config(optimal)
        profiles.append(optimal)
        
        print()
        warning("Alternative ÉCONOMIQUE (utilise moins de RAM):")
        economique = calculate_limits(2500, "ÉCONOMIQUE")
        display_config(economique)
        profiles.append(economique)
        
    elif total_ram_gb >= 4:
        success(f"Serveur avec ressources moyennes détecté ({total_ram_gb} GB)")
        print()
        
        recommande = calculate_limits(2500, "RECOMMANDÉ")
        display_config(recommande)
        profiles.append(recommande)
        
        print()
        warning("Alternative MINIMAL (si d'autres services utilisent la RAM):")
        minimal = calculate_limits(1300, "MINIMAL")
        display_config(minimal)
        profiles.append(minimal)
        
    elif total_ram_gb >= 2:
        warning(f"Serveur avec ressources limitées détecté ({total_ram_gb} GB)")
        print()
        
        minimal = calculate_limits(1300, "MINIMAL (Recommandé)")
        display_config(minimal)
        profiles.append(minimal)
        
        print()
        error("⚠️  Attention: 2 GB RAM est le strict minimum")
        info("Considérez une mise à niveau du serveur pour de meilleures performances")
        
    else:
        error(f"RAM insuffisante détectée ({total_ram_gb} GB)")
        print()
        error("⚠️  Minimum absolu requis: 2 GB RAM")
        error("Votre serveur n'a pas assez de ressources pour ce projet")
        print()
        info("Options:")
        info("  1. Mettre à niveau le serveur (recommandé)")
        info("  2. Ne pas utiliser Celery (désactiver les tâches asynchrones)")
        info("  3. Utiliser un service Redis externe (Redis Cloud, AWS ElastiCache)")
        return
    
    # Instructions
    print()
    header("Instructions d'application")
    print()
    info("1. Choisissez un profil ci-dessus")
    info("2. Copiez les valeurs dans votre fichier .env")
    print()
    info("3. Redémarrez les services Docker:")
    print("   docker-compose down && docker-compose up -d")
    print()
    info("4. Surveillez l'utilisation mémoire:")
    print("   docker stats")
    print()
    
    # Application automatique
    if os.path.exists('.env'):
        header("Application automatique")
        print()
        warning("Fichier .env détecté")
        response = input("Voulez-vous appliquer automatiquement un profil? (y/n): ")
        
        if response.lower() in ['y', 'yes', 'o', 'oui']:
            print()
            print("Choisissez un profil:")
            for i, profile in enumerate(profiles, 1):
                print(f"  {i}) {profile['profile']} ({profile['total']} MB)")
            print(f"  {len(profiles) + 1}) Annuler")
            
            try:
                choice = int(input("\nVotre choix: "))
                if 1 <= choice <= len(profiles):
                    selected = profiles[choice - 1]
                    print()
                    if apply_to_env(selected):
                        print()
                        info("Redémarrez maintenant les services:")
                        print(f"   {Fore.BLUE}docker-compose down && docker-compose up -d{Style.RESET_ALL}")
                else:
                    info("Annulé")
            except ValueError:
                error("Choix invalide")
    
    print()
    header("Notes importantes")
    print()
    warning("- Ces calculs sont des ESTIMATIONS basées sur un usage typique")
    warning("- Surveillez docker stats après le déploiement")
    warning("- Ajustez si vous voyez des OOMKilled ou des performances dégradées")
    warning("- Pour une haute disponibilité, utilisez un profil ÉCONOMIQUE")
    print()
    info("💡 Pour désactiver toutes les limites (déconseillé):")
    print("   Commentez toutes les variables *_MEM_LIMIT dans .env")
    print()
    info("📚 Documentation complète: DEPLOY_SECURITY_FIX.md")
    print()
    success("Script terminé")
    print()

if __name__ == '__main__':
    main()
