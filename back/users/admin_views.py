from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import IsAdminOrStaffReadOnly
from .models import User
from .serializers import AdminUserSerializer, UserSerializer
from installations.models import TechnicalVisit, InstallationCompleted, RepresentationMandate
from billing.models import Quote
from invoices.models import Invoice
from administrative.models import Cerfa16702, EnedisMandate, Consuel
from django.db.models import F
from django.conf import settings
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
class AdminUserViewSet(viewsets.ModelViewSet):
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
    permission_classes = [IsAdminOrStaffReadOnly]
    
    def get_queryset(self):
        """Filtre les utilisateurs selon les besoins"""
        user = self.request.user
        base_qs = User.objects.select_related('useraccess')

        # Logique d'accès selon le rôle
        if user.is_superuser:
            queryset = base_qs
        elif user.is_staff:
            # Pour un staff (collaborateur/commercial): voir les clients dont la demande a source ou assigned_to = user
            # OU les clients qui lui sont affectés en tant qu'installateur
            from django.db.models import Q
            queryset = (
                base_qs
                .filter(
                    Q(installations__offer__request__source=user) |  # Source = collaborateur/client apporteur
                    Q(installations__offer__request__assigned_to=user) |  # Assigned_to = commercial
                    Q(installations__affected_user=user)  # Installateur affecté
                )
                .filter(role=User.UserRoles.CUSTOMER)
                .distinct()
            )
        else:
            # Par défaut, pas d'accès (le permission_class devrait déjà bloquer ces cas)
            queryset = base_qs.none()

        # Filtrage par statut actif/inactif
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        # Filtrage par rôle
        is_staff_param = self.request.query_params.get('is_staff', None)
        if is_staff_param is not None:
            queryset = queryset.filter(is_staff=is_staff_param.lower() == 'true')
        
        # Filtrage par rôle spécifique
        role_param = self.request.query_params.get('role', None)
        if role_param is not None:
            queryset = queryset.filter(role=role_param)

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
        summary="Fiche client détaillée",
        description=(
            "Récupère les informations essentielles d'un client : "
            "informations personnelles, dernière installation, dernier mandat, commission et filleuls"
        )
    )
    @action(detail=True, methods=['get'], url_path='fiche')
    def fiche_client(self, request, pk=None):
        """Récupère la fiche client complète avec toutes les informations associées"""
        user = self.get_object()
        
        # Autorisations: l'admin/staff peut tout voir. Un client peut voir sa propre fiche.
        if not request.user.is_staff and request.user.id != user.id:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        
        from installations.models import RepresentationMandate
        
        # Informations de base de l'utilisateur
        user_data = UserSerializer(user).data
        
        # Nombre total d'installations
        installations_count = user.installations.count()
        
        # Dernière installation
        last_installation = user.installations.order_by('-created_at').first()
        last_installation_data = None
        if last_installation:
            last_installation_data = {
                'id': str(last_installation.id),
                'status': last_installation.status,
                'client_address': last_installation.client_address,
                'installation_power': str(last_installation.installation_power),
                'installation_type': last_installation.installation_type,
                'commission_amount': str(last_installation.commission_amount),
                'commission_paid': last_installation.commission_paid,
                'sales_commission_amount': str(last_installation.sales_commission_amount),
                'sales_commission_paid': last_installation.sales_commission_paid,
                'created_at': last_installation.created_at.isoformat(),
            }
        
        # Dernier mandat de représentation
        last_mandate = None
        if last_installation:
            try:
                mandate = last_installation.representation_mandate
                last_mandate = {
                    'client_civility': mandate.client_civility,
                    'client_birth_date': mandate.client_birth_date.isoformat() if mandate.client_birth_date else None,
                    'client_birth_place': mandate.client_birth_place,
                    'client_address': mandate.client_address,
                }
            except RepresentationMandate.DoesNotExist:
                pass
        
        # Filleuls (clients dont l'utilisateur est la source dans la demande prospect)
        filleuls_count = 0
        filleuls_data = []
        if request.user.is_superuser:  # Uniquement pour l'admin
            from request.models import ProspectRequest
            # Récupérer les demandes où l'utilisateur est la source
            filleul_requests = ProspectRequest.objects.filter(
                source=user,
                offer__isnull=False
            ).select_related('offer__installations_form__client').distinct()
            
            filleuls = []
            for req in filleul_requests:
                if req.offer and hasattr(req.offer, 'installations_form') and req.offer.installations_form.client:
                    client = req.offer.installations_form.client
                    if client not in filleuls:
                        filleuls.append(client)
            
            filleuls_count = len(filleuls)
            for filleul in filleuls:
                filleuls_data.append({
                    'id': str(filleul.id),
                    'first_name': filleul.first_name,
                    'last_name': filleul.last_name,
                    'email': filleul.email,
                })
        
        # Construire la réponse
        response_data = {
            'user': user_data,
            'installations_count': installations_count,
            'last_installation': last_installation_data,
            'last_mandate': last_mandate,
            'filleuls_count': filleuls_count,
            'filleuls': filleuls_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
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
