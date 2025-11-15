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
        user = request.user
        if not user.is_authenticated:
            return False
        # Autorise si l'utilisateur a l'accès administrative ou est superuser
        try:
            return bool(getattr(user.useraccess, 'administrative_procedures', False)) or bool(user.is_superuser)
        except Exception:
            return bool(user.is_superuser)