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