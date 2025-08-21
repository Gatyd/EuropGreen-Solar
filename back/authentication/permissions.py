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