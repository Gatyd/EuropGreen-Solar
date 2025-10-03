"""
Middleware custom pour synchroniser l'utilisateur authentifié avec auditlog.

Le middleware AuditlogMiddleware par défaut ne fonctionne pas avec l'authentification JWT cookie,
car il cherche request.user qui n'est défini que par DRF dans les vues API.

Ce middleware définit explicitement l'actor pour auditlog en utilisant set_actor.
"""
from auditlog.context import set_actor
from authentication.auth_method import CookieJWTAuthentication


class AuditlogActorMiddleware:
    """
    Middleware qui définit l'actor pour auditlog en utilisant l'authentification JWT cookie.
    
    Doit être placé APRÈS AuthenticationMiddleware et AVANT AuditlogMiddleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = CookieJWTAuthentication()
    
    def __call__(self, request):
        # Essayer d'authentifier via JWT cookie
        auth_result = self.auth.authenticate(request)
        
        if auth_result:
            user, _ = auth_result
            # Définir l'actor pour auditlog
            set_actor(user)
            # Définir aussi request.user pour cohérence
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                request.user = user
        
        response = self.get_response(request)
        return response
