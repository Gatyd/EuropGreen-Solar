from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import IsAdmin
from .models import User
from .serializers import UserSerializer, AdminUserSerializer, ChangePasswordSerializer
from installations.models import Form as InstallationForm, TechnicalVisit, InstallationCompleted, RepresentationMandate
from billing.models import Quote
from invoices.models import Invoice
from administrative.models import Cerfa16702, EnedisMandate, Consuel
from django.db.models import F

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
        queryset = User.objects.select_related('useraccess')

        # Filtrage par statut actif/inactif
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filtrage par rôle
        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')

        return queryset

    @extend_schema(
        summary="Documents liés à un utilisateur",
        description="Retourne les documents (pdf/id) liés aux fiches d'installation du client, groupés par type."
    )
    @action(detail=True, methods=['get'], url_path='documents')
    def documents(self, request, pk=None):
        user = self.get_object()
        # Ne renvoyer que pour les non-staff (clients). Pour d'autres rôles, on peut autoriser admin seulement
        if not request.user.is_staff and request.user.id != user.id:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer les formulaires d'installation du client
        forms_qs = InstallationForm.objects.filter(client=user).only('id', 'offer_id')

        # Quotes liés aux offers de ces forms
        quotes = Quote.objects.filter(offer__installations_form__client=user, pdf__isnull=False).values('id', 'pdf')
        # Invoices liés aux forms
        invoices = Invoice.objects.filter(installation__client=user, pdf__isnull=False).values('id', 'pdf')
        # CERFA 16702
        cerfas = Cerfa16702.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
        # Mandat de représentation (installations)
        rep_mandates = RepresentationMandate.objects.filter(form__client=user, mandate_pdf__isnull=False).values('id', pdf=F('mandate_pdf'))
        # Consuels
        consuels = Consuel.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
        # Mandat Enedis
        enedis_mandates = EnedisMandate.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
        # Rapports
        tech_reports = TechnicalVisit.objects.filter(form__client=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))
        install_reports = InstallationCompleted.objects.filter(form__client=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))

        # Construction de la réponse minimale (id, pdf path)
        payload = {
            'quotes': list(quotes),
            'invoices': list(invoices),
            'cerfa16702': list(cerfas),
            'representation_mandates': list(rep_mandates),
            'consuels': list(consuels),
            'enedis_mandates': list(enedis_mandates),
            'technical_visit_reports': list(tech_reports),
            'installation_reports': list(install_reports),
        }
        return Response(payload, status=status.HTTP_200_OK)
    
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
    