import logging
import traceback

logger = logging.getLogger('administrative')


class DebugCerfaMiddleware:
    """Middleware pour déboguer les erreurs 500 sur les routes CERFA."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log avant traitement si c'est une route CERFA
        if '/administrative/cerfa16702/' in request.path:
            logger.error(f"🟢 MIDDLEWARE: {request.method} {request.path}")
            logger.error(f"🟢 User: {request.user if hasattr(request, 'user') else 'N/A'}")
            logger.error(f"🟢 Content-Type: {request.content_type}")
        
        response = self.get_response(request)
        
        # Log après traitement si erreur 500
        if response.status_code == 500 and '/administrative/cerfa16702/' in request.path:
            logger.error(f"🔴 MIDDLEWARE: Response 500 for {request.path}")
            logger.error(f"🔴 Response content: {response.content[:500] if hasattr(response, 'content') else 'N/A'}")
        
        return response

    def process_exception(self, request, exception):
        """Capture toutes les exceptions non gérées."""
        if '/administrative/cerfa16702/' in request.path:
            logger.error(f"🔴🔴🔴 UNCAUGHT EXCEPTION in {request.path}")
            logger.error(f"🔴 Exception type: {type(exception).__name__}")
            logger.error(f"🔴 Exception message: {str(exception)}")
            logger.error(f"🔴 Traceback:\n{traceback.format_exc()}")
        return None  # Laisser Django gérer l'exception normalement
