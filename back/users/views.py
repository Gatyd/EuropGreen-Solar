from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import IsAdmin
from .models import User, UserAccess
from .serializers import UserSerializer, AdminUserSerializer, ChangePasswordSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Liste des utilisateurs",
        description="Récupère la liste de tous les utilisateurs avec leurs droits d'accès"
    ),
    create=extend_schema(
        summary="Créer un utilisateur",
        description="Crée un nouvel utilisateur avec génération automatique d'un mot de passe sécurisé et envoi par email"
    ),
    retrieve=extend_schema(
        summary="Détails d'un utilisateur",
        description="Récupère les détails d'un utilisateur spécifique avec ses droits d'accès"
    ),
    partial_update=extend_schema(
        summary="Modification partielle d'un utilisateur",
        description="Met à jour partiellement les informations d'un utilisateur et ses droits d'accès"
    )
)
class AdminUserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    
    Ce ViewSet fournit les actions suivantes :
    - list: Liste tous les utilisateurs
    - create: Crée un nouvel utilisateur avec mot de passe auto-généré
    - retrieve: Récupère un utilisateur spécifique
    - partial_update: Met à jour un utilisateur et ses droits d'accès
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post', 'patch']
    
    def get_queryset(self):
        """Filtre les utilisateurs selon les besoins"""
        queryset = User.objects.select_related('useraccess').filter(is_staff=True)

        # Filtrage par statut actif/inactif
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filtrage par rôle
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
            
        return queryset
    
    @extend_schema(
        summary="Désactiver un utilisateur",
        description="Désactive un utilisateur (ne le supprime pas définitivement)"
    )
    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """Désactive un utilisateur"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(
            {
                "message": "Utilisateur désactivé avec succès",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Réactiver un utilisateur",
        description="Réactive un utilisateur précédemment désactivé"
    )
    @action(detail=True, methods=['patch'])
    def reactivate(self, request, pk=None):
        """Réactive un utilisateur désactivé"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(
            {
                "message": "Utilisateur réactivé avec succès",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )

class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour les opérations sur l'utilisateur connecté.
    
    Permet de récupérer et mettre à jour les informations de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    @extend_schema(
        summary="Désactiver l'utilisateur connecté",
        description="Désactive l'utilisateur connecté (ne le supprime pas définitivement)"
    )
    @action(detail=False, methods=['patch'])
    def deactivate(self, request, pk=None):
        user = request.user
        user.is_active = False
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(
            {
                "message": "Utilisateur désactivé avec succès",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Réactiver l'utilisateur connecté",
        description="Réactive l'utilisateur connecté précédemment désactivé"
    )
    @action(detail=False, methods=['patch'])
    def reactivate(self, request, pk=None):
        user = request.user
        user.is_active = True
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(
            {
                "message": "Utilisateur réactivé avec succès",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Changer le mot de passe de l'utilisateur connecté",
        description="Permet à l'utilisateur connecté de changer son mot de passe en fournissant l'ancien et le nouveau",
        request=ChangePasswordSerializer,
        responses={200: {"description": "Mot de passe changé avec succès"}}
    )
    @action(detail=False, methods=['patch'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request, pk=None):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request, 'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Mot de passe changé avec succès"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        summary="Profil utilisateur connecté",
        description="Récupère les informations de l'utilisateur actuellement connecté"
    )
    def get(self, request):
        """Récupère les informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Modifier le profil utilisateur de l'utilisateur connecté",
        description="Met à jour les informations de l'utilisateur connecté"
    )
    @action(detail=False, methods=['patch'])
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    