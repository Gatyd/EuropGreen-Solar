"""
Exception handler personnalisé pour DRF.
Log automatiquement le stacktrace complet de toutes les erreurs serveur (500).
"""
import logging
import traceback
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Exception handler personnalisé qui log le stacktrace complet pour toutes les erreurs serveur.
    
    Args:
        exc: L'exception levée
        context: Le contexte de la requête (view, request, args, kwargs)
    
    Returns:
        Response: La réponse DRF standard
    """
    # Appeler le handler par défaut de DRF
    response = drf_exception_handler(exc, context)
    
    # Si c'est une erreur serveur (500) ou une exception non gérée par DRF
    if response is None or (response and response.status_code >= 500):
        # Extraire les informations de contexte
        request = context.get('request')
        view = context.get('view')
        
        # Construire le message de log
        error_details = {
            'exception_type': type(exc).__name__,
            'exception_message': str(exc),
            'path': request.path if request else 'N/A',
            'method': request.method if request else 'N/A',
            'user': str(request.user) if request and hasattr(request, 'user') else 'AnonymousUser',
            'view': view.__class__.__name__ if view else 'N/A',
        }
        
        # Logger l'erreur avec le stacktrace complet
        logger.error(
            f"❌ EXCEPTION SERVEUR: {error_details['exception_type']}: {error_details['exception_message']}\n"
            f"   Path: {error_details['method']} {error_details['path']}\n"
            f"   User: {error_details['user']}\n"
            f"   View: {error_details['view']}\n"
            f"\n📋 STACKTRACE:\n{traceback.format_exc()}"
        )
    
    return response
