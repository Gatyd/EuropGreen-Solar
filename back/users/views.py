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
from django.conf import settings
from EuropGreenSolar.email_utils import send_mail
from django.core.files.storage import default_storage

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
        description=(
            "Retourne les documents (pdf/id) groupés par type.\n"
            "- Si l'utilisateur est un client: documents liés à ses fiches d'installation.\n"
            "- Sinon (employé/installeur/admin): documents qu'il a créés (created_by).\n"
            "Possibilité de forcer le comportement via ?mode=client|created."
        )
    )
    @action(detail=True, methods=['get'], url_path='documents')
    def documents(self, request, pk=None):
        user = self.get_object()
        # Autorisations: l'admin peut tout voir. Un utilisateur peut voir ses propres docs.
        if not request.user.is_staff and request.user.id != user.id:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        mode = (request.query_params.get('mode') or '').strip().lower()
        is_client = (user.role == User.UserRoles.CUSTOMER)
        use_client_mode = (mode == 'client') or (mode == '' and is_client)

        if use_client_mode:
            # Documents liés aux fiches du client
            quotes = Quote.objects.filter(offer__installations_form__client=user, pdf__isnull=False).values('id', 'pdf')
            invoices = Invoice.objects.filter(installation__client=user, pdf__isnull=False).values('id', 'pdf')
            cerfas = Cerfa16702.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
            rep_mandates = RepresentationMandate.objects.filter(form__client=user, mandate_pdf__isnull=False).values('id', pdf=F('mandate_pdf'))
            consuels = Consuel.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
            enedis_mandates = EnedisMandate.objects.filter(form__client=user, pdf__isnull=False).values('id', 'pdf')
            tech_reports = TechnicalVisit.objects.filter(form__client=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))
            install_reports = InstallationCompleted.objects.filter(form__client=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))
        else:
            # Documents créés par l'utilisateur (non-client, ou mode=created forcé)
            quotes = Quote.objects.filter(created_by=user, pdf__isnull=False).values('id', 'pdf')
            invoices = Invoice.objects.filter(created_by=user, pdf__isnull=False).values('id', 'pdf')
            cerfas = Cerfa16702.objects.filter(created_by=user, pdf__isnull=False).values('id', 'pdf')
            rep_mandates = RepresentationMandate.objects.filter(created_by=user, mandate_pdf__isnull=False).values('id', pdf=F('mandate_pdf'))
            consuels = Consuel.objects.filter(created_by=user, pdf__isnull=False).values('id', 'pdf')
            enedis_mandates = EnedisMandate.objects.filter(created_by=user, pdf__isnull=False).values('id', 'pdf')
            tech_reports = TechnicalVisit.objects.filter(created_by=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))
            install_reports = InstallationCompleted.objects.filter(created_by=user, report_pdf__isnull=False).values('id', pdf=F('report_pdf'))

        # Helper: transforme les chemins de fichiers en URLs absolues incluant le host
        def with_absolute_pdf(items):
            result = []
            for d in list(items):
                # d est un dict {'id': ..., 'pdf': 'path/in/media.ext'}
                name = d.get('pdf')
                if name:
                    try:
                        # Respecte le backend de stockage (local/S3…)
                        url = default_storage.url(name)
                    except Exception:
                        # Fallback simple si le storage ne fournit pas d'URL
                        url = f"{getattr(settings, 'MEDIA_URL', '/media/')}{name}"

                    if isinstance(url, str) and (url.startswith('http://') or url.startswith('https://')):
                        abs_url = url
                    else:
                        abs_url = request.build_absolute_uri(url)
                    d['pdf'] = abs_url
                result.append(d)
            return result

        # Construction de la réponse minimale (id, pdf url absolue)
        payload = {
            'quotes': with_absolute_pdf(quotes),
            'invoices': with_absolute_pdf(invoices),
            'cerfa16702': with_absolute_pdf(cerfas),
            'representation_mandates': with_absolute_pdf(rep_mandates),
            'consuels': with_absolute_pdf(consuels),
            'enedis_mandates': with_absolute_pdf(enedis_mandates),
            'technical_visit_reports': with_absolute_pdf(tech_reports),
            'installation_reports': with_absolute_pdf(install_reports),
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
