from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur est un administrateur.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser
    
class IsAdminOrStaffReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur est un administrateur ou un membre du personnel avec accès en lecture seule.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if user.is_staff and request.method in permissions.SAFE_METHODS:
            return True
        return False

class HasRequestsAccess(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur a accès aux requêtes.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Autorise si l'utilisateur a l'accès requests ou est superuser
        try:
            return bool(getattr(user.useraccess, 'requests', False)) or bool(user.is_superuser)
        except Exception:
            return bool(user.is_superuser)

class HasOfferAccess(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur a accès aux offres.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Autorise si l'utilisateur a l'accès offers ou est superuser
        try:
            return bool(getattr(user.useraccess, 'offers', False)) or bool(user.is_superuser)
        except Exception:
            return bool(user.is_superuser)

class HasInstallationAccess(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur a accès aux installations.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Autorise si l'utilisateur a l'accès installations ou est superuser
        try:
            return bool(getattr(user.useraccess, 'installation', False)) or bool(user.is_superuser)
        except Exception:
            return bool(user.is_superuser)
        
class HasAdministrativeAccess(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur a accès aux fonctionnalités administratives.
    """

    def has_permission(self, request, view):
        import logging
        import sys
        logger = logging.getLogger(__name__)
        user = request.user
        
        print(f"🔵 HasAdministrativeAccess check for user: {user} (authenticated: {user.is_authenticated})", file=sys.stderr, flush=True)
        logger.error(f"🔵 HasAdministrativeAccess check for user: {user} (authenticated: {user.is_authenticated})")
        
        if not user.is_authenticated:
            print(f"🔵 Permission DENIED: User not authenticated", file=sys.stderr, flush=True)
            logger.error(f"🔵 Permission DENIED: User not authenticated")
            return False
        # Autorise si l'utilisateur a l'accès administrative ou est superuser
        try:
            has_access = bool(getattr(user.useraccess, 'administrative_procedures', False)) or bool(user.is_superuser)
            print(f"🔵 Permission result: {has_access} (is_superuser: {user.is_superuser}, administrative_procedures: {getattr(user.useraccess, 'administrative_procedures', 'N/A')})", file=sys.stderr, flush=True)
            logger.error(f"🔵 Permission result: {has_access} (is_superuser: {user.is_superuser}, administrative_procedures: {getattr(user.useraccess, 'administrative_procedures', 'N/A')})")
            return has_access
        except Exception as e:
            print(f"🔵 Permission check exception: {e}", file=sys.stderr, flush=True)
            logger.error(f"🔵 Permission check exception: {e}")
            result = bool(user.is_superuser)
            print(f"🔵 Fallback to is_superuser: {result}", file=sys.stderr, flush=True)
            logger.error(f"🔵 Fallback to is_superuser: {result}")
            return result