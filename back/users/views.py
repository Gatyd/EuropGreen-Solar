from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import User, UserAccess
from .serializers import UserSerializer, UserAccessUpdateSerializer, ChangePasswordSerializer

def test_mail(request):
    """Test function to render a template for email testing"""
    from django.shortcuts import render
    from django.conf import settings
    
    # Paramètre pour tester différents types d'utilisateurs
    user_type = request.GET.get('type', 'employee')
    
    if user_type == 'admin':
        context = {
            'user': {
                'first_name': 'Marie',
                'last_name': 'Dupont',
                'email': 'marie.dupont@europgreensolar.com',
                'role': 'admin',
                'is_superuser': True,
                'get_role_display': 'Administrateur',
            },
            'password': 'Temp2024@Admin',
            'frontend_url': settings.FRONTEND_URL,
        }
    elif user_type == 'secretary':
        context = {
            'user': {
                'first_name': 'Sophie',
                'last_name': 'Martin',
                'email': 'sophie.martin@europgreensolar.com',
                'role': 'secretary',
                'is_superuser': False,
                'get_role_display': 'Secrétaire',
                'useraccess': {
                    'installation': False,
                    'offers': True,
                    'requests': True,
                    'administrative_procedures': True
                },
            },
            'password': 'Temp2024@Sec',
            'frontend_url': settings.FRONTEND_URL,
        }
    elif user_type == 'installer':
        context = {
            'user': {
                'first_name': 'Pierre',
                'last_name': 'Leroy',
                'email': 'pierre.leroy@europgreensolar.com',
                'role': 'installer',
                'is_superuser': False,
                'get_role_display': 'Installateur',
                'useraccess': {
                    'installation': True,
                    'offers': False,
                    'requests': True,
                    'administrative_procedures': False
                },
            },
            'password': 'Temp2024@Install',
            'frontend_url': settings.FRONTEND_URL,
        }
    else:  # employee par défaut
        context = {
            'user': {
                'first_name': 'Jean',
                'last_name': 'Moreau',
                'email': 'jean.moreau@europgreensolar.com',
                'role': 'employee',
                'is_superuser': False,
                'get_role_display': 'Employé',
                'useraccess': {
                    'installation': True,
                    'offers': True,
                    'requests': False,
                    'administrative_procedures': False
                },
            },
            'password': 'Temp2024@Emp',
            'frontend_url': settings.FRONTEND_URL,
        }
    
    return render(request, 'emails/welcome_user.html', context)

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
class UserViewSet(mixins.ListModelMixin,
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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']  # Limite aux méthodes autorisées
    
    def get_queryset(self):
        """Filtre les utilisateurs selon les besoins"""
        queryset = User.objects.select_related('useraccess').all()
        
        # Filtrage par statut actif/inactif
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filtrage par rôle
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
            
        return queryset
    
    def perform_update(self, serializer):
        """Gère la mise à jour d'un utilisateur et de ses droits d'accès"""
        # Récupération des données d'accès depuis la requête
        access_data = self.request.data.get('access', None)
        
        # Sauvegarde de l'utilisateur
        user = serializer.save()
        
        # Mise à jour des droits d'accès si fournis et si l'utilisateur n'est pas client ou admin
        if access_data is not None and user.role not in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            user_access, created = UserAccess.objects.get_or_create(user=user)
            access_serializer = UserAccessUpdateSerializer(user_access, data=access_data, partial=True)
            if access_serializer.is_valid():
                access_serializer.save()
        elif user.role in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            # Supprime les accès existants si l'utilisateur devient client ou admin
            UserAccess.objects.filter(user=user).delete()
    
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
    
    @extend_schema(
        summary="Changer le mot de passe",
        description="Permet à un utilisateur de changer son mot de passe en fournissant l'ancien et le nouveau",
        request=ChangePasswordSerializer,
        responses={200: {"description": "Mot de passe changé avec succès"}}
    )
    @action(detail=True, methods=['patch'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request, pk=None):
        """Change le mot de passe d'un utilisateur après validation de l'ancien"""
        user = self.get_object()
        
        # Utilise le serializer dédié au changement de mot de passe
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request, 'user': user})
        
        if serializer.is_valid():
            # Le serializer gère la validation et la sauvegarde
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


@extend_schema(
    summary="Profil utilisateur connecté",
    description="Récupère les informations de l'utilisateur actuellement connecté"
)
class CurrentUserView(APIView):
    """Vue pour récupérer les informations de l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retourne les informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
