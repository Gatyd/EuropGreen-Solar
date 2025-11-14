import logging
import traceback
import sys

logger = logging.getLogger('administrative')


class DebugCerfaMiddleware:
    """Middleware pour déboguer les erreurs 500 sur les routes CERFA."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log avant traitement si c'est une route CERFA
        if '/administrative/cerfa16702/' in request.path:
            # Forcer l'affichage avec print + flush pour Gunicorn
            print(f"🟢 MIDDLEWARE: {request.method} {request.path}", file=sys.stderr, flush=True)
            print(f"🟢 User: {request.user if hasattr(request, 'user') else 'N/A'}", file=sys.stderr, flush=True)
            print(f"🟢 Content-Type: {request.content_type}", file=sys.stderr, flush=True)
            logger.error(f"🟢 MIDDLEWARE: {request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log après traitement si erreur 500
        if response.status_code == 500 and '/administrative/cerfa16702/' in request.path:
            print(f"🔴 MIDDLEWARE: Response 500 for {request.path}", file=sys.stderr, flush=True)
            print(f"🔴 Response content: {response.content[:500] if hasattr(response, 'content') else 'N/A'}", file=sys.stderr, flush=True)
            logger.error(f"🔴 MIDDLEWARE: Response 500 for {request.path}")
        
        return response

    def process_exception(self, request, exception):
        """Capture toutes les exceptions non gérées."""
        if '/administrative/cerfa16702/' in request.path:
            print(f"🔴🔴🔴 UNCAUGHT EXCEPTION in {request.path}", file=sys.stderr, flush=True)
            print(f"🔴 Exception type: {type(exception).__name__}", file=sys.stderr, flush=True)
            print(f"🔴 Exception message: {str(exception)}", file=sys.stderr, flush=True)
            print(f"🔴 Traceback:\n{traceback.format_exc()}", file=sys.stderr, flush=True)
            logger.error(f"🔴🔴🔴 UNCAUGHT EXCEPTION in {request.path}")
            logger.error(f"🔴 Traceback:\n{traceback.format_exc()}")
        return None  # Laisser Django gérer l'exception normalement
