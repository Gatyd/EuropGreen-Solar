"""
Script de test de la sécurité Redis
Usage: python test_redis_security.py
"""

import os
import sys
import redis
from decouple import config
from colorama import Fore, Style, init

# Initialiser colorama pour Windows
init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def test_redis_connection():
    """Test de connexion Redis avec authentification"""
    print_header("Test 1: Connexion Redis avec authentification")
    
    try:
        # Récupérer la config depuis les variables d'environnement
        redis_password = config('REDIS_PASSWORD', default='')
        redis_host = config('REDIS_HOST', default='localhost')
        redis_port = config('REDIS_PORT', default='6379', cast=int)
        redis_db = config('REDIS_DB', default='0', cast=int)
        
        print_info(f"Connexion à Redis: {redis_host}:{redis_port}/{redis_db}")
        
        if not redis_password:
            print_warning("REDIS_PASSWORD non défini dans .env")
            print_info("Tentative de connexion sans authentification...")
        
        # Construire l'URL Redis
        if redis_password:
            redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        
        # Connexion
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Test PING
        response = r.ping()
        if response:
            print_success("Redis répond correctement (PING → PONG)")
            return True, r
        else:
            print_error("Redis ne répond pas correctement")
            return False, None
            
    except redis.exceptions.AuthenticationError:
        print_error("Erreur d'authentification Redis")
        print_info("Vérifiez que REDIS_PASSWORD dans .env correspond au mot de passe Redis")
        return False, None
    except redis.exceptions.ConnectionError as e:
        print_error(f"Impossible de se connecter à Redis: {e}")
        print_info("Vérifiez que Redis est démarré (docker-compose ps)")
        return False, None
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False, None

def test_redis_security(r):
    """Test des mesures de sécurité Redis"""
    print_header("Test 2: Vérification des mesures de sécurité")
    
    if r is None:
        print_warning("Connexion Redis non disponible, test ignoré")
        return
    
    # Test 1: Commande CONFIG désactivée
    try:
        r.config_get('*')
        print_error("Commande CONFIG toujours active (vulnérabilité)")
    except redis.exceptions.ResponseError as e:
        if "unknown command" in str(e).lower() or "renamed" in str(e).lower():
            print_success("Commande CONFIG désactivée (sécurisé)")
        else:
            print_warning(f"CONFIG retourne une erreur: {e}")
    
    # Test 2: Info mémoire
    try:
        info = r.info('memory')
        used_memory_mb = info['used_memory'] / (1024 * 1024)
        maxmemory_mb = info.get('maxmemory', 0) / (1024 * 1024)
        
        print_info(f"Mémoire utilisée: {used_memory_mb:.2f} MB")
        
        if maxmemory_mb > 0:
            print_success(f"Limite mémoire configurée: {maxmemory_mb:.2f} MB")
            print_info(f"Utilisation: {(used_memory_mb / maxmemory_mb * 100):.1f}%")
        else:
            print_warning("Aucune limite mémoire configurée (risque OOM)")
    except Exception as e:
        print_warning(f"Impossible de récupérer les infos mémoire: {e}")
    
    # Test 3: Politique d'éviction
    try:
        config = r.config_get('maxmemory-policy')
        policy = config.get('maxmemory-policy', 'noeviction')
        
        if policy in ['allkeys-lru', 'allkeys-lfu']:
            print_success(f"Politique d'éviction configurée: {policy}")
        else:
            print_warning(f"Politique d'éviction: {policy} (recommandé: allkeys-lru)")
    except redis.exceptions.ResponseError:
        print_info("CONFIG GET désactivé, impossible de vérifier la politique")

def test_celery_broker():
    """Test de connexion Celery au broker Redis"""
    print_header("Test 3: Connexion Celery au broker Redis")
    
    try:
        # Import Django settings
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EuropGreenSolar.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        from celery import Celery
        
        print_info(f"Broker URL: {settings.CELERY_BROKER_URL.replace(':' + settings.REDIS_PASSWORD + '@', ':***@')}")
        
        # Créer une instance Celery
        app = Celery(broker=settings.CELERY_BROKER_URL)
        
        # Tester la connexion
        inspect = app.control.inspect()
        active = inspect.active()
        
        if active is not None:
            print_success("Celery se connecte correctement au broker Redis")
            
            # Afficher les workers actifs
            if active:
                print_info(f"Workers actifs: {len(active)}")
                for worker_name, tasks in active.items():
                    print_info(f"  - {worker_name}: {len(tasks)} tâches en cours")
            else:
                print_warning("Aucun worker Celery actif")
        else:
            print_error("Impossible de communiquer avec les workers Celery")
            print_info("Vérifiez que celery-worker est démarré")
        
        return True
        
    except ImportError as e:
        print_error(f"Impossible d'importer Django/Celery: {e}")
        print_info("Exécutez ce script depuis le conteneur ou installez les dépendances")
        return False
    except Exception as e:
        print_error(f"Erreur lors du test Celery: {e}")
        return False

def test_redis_data():
    """Test d'écriture/lecture Redis"""
    print_header("Test 4: Lecture/Écriture Redis")
    
    try:
        redis_password = config('REDIS_PASSWORD', default='')
        redis_host = config('REDIS_HOST', default='localhost')
        redis_port = config('REDIS_PORT', default='6379', cast=int)
        
        if redis_password:
            redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
        else:
            redis_url = f"redis://{redis_host}:{redis_port}/0"
        
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Test SET
        test_key = "test:security:check"
        test_value = "EuropGreen-Solar Security Test"
        
        r.set(test_key, test_value, ex=60)  # Expire après 60s
        print_success("Écriture Redis réussie")
        
        # Test GET
        retrieved = r.get(test_key)
        if retrieved == test_value:
            print_success("Lecture Redis réussie")
        else:
            print_error(f"Valeur incorrecte: attendu '{test_value}', obtenu '{retrieved}'")
        
        # Test DEL
        r.delete(test_key)
        print_success("Suppression Redis réussie")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur lors du test lecture/écriture: {e}")
        return False

def check_environment():
    """Vérifier les variables d'environnement"""
    print_header("Configuration des variables d'environnement")
    
    required_vars = {
        'REDIS_PASSWORD': 'Mot de passe Redis',
        'REDIS_HOST': 'Hôte Redis',
        'REDIS_PORT': 'Port Redis',
        'REDIS_DB': 'Base de données Redis',
    }
    
    all_ok = True
    
    for var_name, description in required_vars.items():
        value = config(var_name, default='')
        
        if value:
            if var_name == 'REDIS_PASSWORD':
                # Masquer le mot de passe
                masked = value[:3] + '*' * (len(value) - 3)
                print_success(f"{description}: {masked}")
                
                # Vérifier la force du mot de passe
                if len(value) < 12:
                    print_warning(f"Mot de passe court ({len(value)} caractères), recommandé: 32+")
                elif value == 'changeme_redis_password' or value == 'changeme_redis_password_MUST_BE_CHANGED':
                    print_error("Mot de passe par défaut détecté! CHANGEZ-LE IMMÉDIATEMENT")
                    all_ok = False
            else:
                print_success(f"{description}: {value}")
        else:
            print_warning(f"{description}: Non défini (utilise la valeur par défaut)")
    
    return all_ok

def main():
    """Fonction principale"""
    print(f"\n{Fore.GREEN}{'*' * 60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}* Test de sécurité Redis - EuropGreen-Solar{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'*' * 60}{Style.RESET_ALL}")
    
    # Vérifier l'environnement
    env_ok = check_environment()
    
    # Test de connexion
    connection_ok, redis_client = test_redis_connection()
    
    # Tests de sécurité
    if connection_ok:
        test_redis_security(redis_client)
        test_redis_data()
    
    # Test Celery
    test_celery_broker()
    
    # Résumé
    print_header("Résumé")
    
    if env_ok and connection_ok:
        print_success("Tous les tests de base sont passés")
        print_info("Vérifiez les warnings ci-dessus pour optimiser la sécurité")
    else:
        print_error("Certains tests ont échoué")
        print_info("Consultez SECURITY_REDIS.md pour les corrections")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    main()
