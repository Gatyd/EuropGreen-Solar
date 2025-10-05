from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAdminUser
from .models import User, Role
from .serializers import UserSerializer, ChangePasswordSerializer, RoleSerializer
from django.conf import settings
from EuropGreenSolar.email_utils import send_mail


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
    
class SupportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Envoyer une demande SAV",
        description="Permet à l'utilisateur connecté d'envoyer une demande SAV. Envoie un email à l'adresse configurée (SAV_EMAIL)",
        request=dict,
        responses={200: {"description": "Demande envoyée"}}
    )
    def post(self, request):
        message = (request.data.get('message') or '').strip()
        category = (request.data.get('category') or '').strip() or None
        if not message:
            return Response({ 'message': 'Ce champ est requis.' }, status=status.HTTP_400_BAD_REQUEST)

        to_email = getattr(settings, 'SAV_EMAIL', None)
        if not to_email:
            return Response({ 'detail': 'Configuration SAV_EMAIL manquante.' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user: User = request.user
        context = {
            'user': user,
            'user_email': user.email,
            'message': message,
        }
        if category:
            context['category'] = category
        try:
            send_mail(
                template='emails/support/support_request.html',
                context=context,
                subject='[SAV] Nouvelle demande client',
                to=to_email,
            )
        except Exception:
            return Response({ 'detail': "Échec d'envoi de l'email" }, status=status.HTTP_502_BAD_GATEWAY)

        return Response({ 'status': 'ok' }, status=status.HTTP_200_OK)


class CareerApplicationView(APIView):
    """Vue pour soumettre une candidature de collaborateur"""
    # Pas d'authentification requise - formulaire public
    permission_classes = []

    @extend_schema(
        summary="Soumettre une candidature",
        description="Permet à un candidat de soumettre sa candidature pour devenir collaborateur. Envoie un email à l'adresse configurée (CAREER_EMAIL)",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'description': 'Prénom du candidat'},
                    'last_name': {'type': 'string', 'description': 'Nom du candidat'},
                    'email': {'type': 'string', 'description': 'Email du candidat'},
                    'phone': {'type': 'string', 'description': 'Téléphone du candidat'},
                    'role': {'type': 'string', 'description': 'Rôle souhaité (optionnel)'},
                    'message': {'type': 'string', 'description': 'Message / Motivations'},
                },
                'required': ['first_name', 'last_name', 'email', 'phone', 'message']
            }
        },
        responses={200: {"description": "Candidature envoyée avec succès"}}
    )
    def post(self, request):
        # Récupération et validation des champs
        first_name = (request.data.get('first_name') or '').strip()
        last_name = (request.data.get('last_name') or '').strip()
        email = (request.data.get('email') or '').strip()
        phone = (request.data.get('phone') or '').strip()
        role = (request.data.get('role') or '').strip() or 'Non spécifié'
        message = (request.data.get('message') or '').strip()
        
        # Validation des champs requis
        if not all([first_name, last_name, email, phone, message]):
            return Response(
                {'detail': 'Tous les champs (prénom, nom, email, téléphone, message) sont requis.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de la configuration email
        to_email = getattr(settings, 'CAREER_EMAIL', None)
        if not to_email:
            return Response(
                {'detail': 'Configuration CAREER_EMAIL manquante.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Préparation du contexte pour le template email
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'role': role,
            'message': message,
        }
        
        # Envoi de l'email
        try:
            send_mail(
                template='emails/career/application.html',
                context=context,
                subject=f'[Candidature] {first_name} {last_name} - {role}',
                to=to_email,
            )
        except Exception as e:
            return Response(
                {'detail': "Échec d'envoi de l'email"}, 
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="Liste des rôles"),
    retrieve=extend_schema(summary="Détail d'un rôle"),
    create=extend_schema(summary="Créer un rôle"),
    partial_update=extend_schema(summary="Mettre à jour partiellement un rôle"),
    destroy=extend_schema(summary="Supprimer un rôle")
)
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        # Permettre lecture aux staff read-only si besoin plus tard, ici strict admin
        return super().get_permissions()
